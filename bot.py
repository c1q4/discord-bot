import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord.ui import View, Button
from datetime import datetime
import io
import os
# .env から TOKEN を読み込む
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # メッセージを読むために必要

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    try:
        synced = await bot.tree.sync()  # スラッシュコマンド同期
        print(f"スラッシュコマンド同期完了: {len(synced)} 個")
    except Exception as e:
        print(e)

# /ping コマンド
@bot.tree.command(name="生存確認", description="Botの生存を確認します")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("生きてます！")

@bot.tree.command(name="ban", description="メンバーをBANします")
@app_commands.describe(
    member="対象",
    reason="理由"
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "無し"
):


    if member == interaction.user:
       await interaction.response.send_message(
        "❌ 自分自身は操作できません。",
        ephemeral=True
         )
       return

    if member.top_role >= interaction.user.top_role:
       await interaction.response.send_message(
        "❌ 自分と同等以上のロールは操作できません。",
        ephemeral=True
        )
       return

    if member.top_role >= interaction.guild.me.top_role:
       await interaction.response.send_message(
        "❌ Botより上のロールは操作できません。",
        ephemeral=True
        )
       return


    # 実行者の権限チェック
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(
            "❌ BAN権限がありません。",
            ephemeral=True
        )
        return

    # Botの権限チェック
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message(
            "❌ BotにBAN権限がありません。",
            ephemeral=True
        )
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(
        f"🚫 **{member}**をBANしました。\n理由：{reason}"
    )
 
    await send_log(
    interaction.guild,
    f"🚫 BAN\n実行者: {interaction.user}\n対象: {member}\n理由: {reason}"
    )


LOG_CHANNEL_ID = 1465703396853026973

@bot.tree.command(name="unban", description="BANを解除します")
@app_commands.describe(user="BAN解除するユーザー")
async def unban(interaction: discord.Interaction, user: discord.User):

    try:
        await interaction.guild.unban(user, reason="Unban command")

        await interaction.response.send_message(
            f"🔓 **{user}** のBANを解除しました。"
        )

        # ログ送信
        channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(f"🔓 {user} がBAN解除されました")

    except discord.NotFound:
        await interaction.response.send_message(
            "❌ そのユーザーはBANされていません。",
            ephemeral=True
        )

@bot.tree.command(name="kick", description="メンバーをサーバーから退出させます")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.checks.bot_has_permissions(kick_members=True)
@app_commands.describe(
    member="対象",
    reason="理由"
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "無し"
):


    if member == interaction.user:
       await interaction.response.send_message(
        "❌ 自分自身はキックできません。",
        ephemeral=True
        )
       return

    if member.top_role >= interaction.user.top_role:
       await interaction.response.send_message(
        "❌ 自分と同等以上のロールは操作できません。",
        ephemeral=True
        )
       return

    if member.top_role >= interaction.guild.me.top_role:
       await interaction.response.send_message(
        "❌ Botより上のロールは操作できません。",
        ephemeral=True
        )
       return



    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 **{member}** をKICKしました\n理由: {reason}"
    )

    await send_log(
        interaction.guild,
        f"👢 KICK\n実行者: {interaction.user}\n対象: {member}\n理由: {reason}"
    )



from datetime import timedelta

@bot.tree.command(name="timeout", description="メンバーをタイムアウトします")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
@app_commands.describe(
    member="対象",
    minutes="タイムアウト時間",
    reason="理由"
)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "無し"
):
    
    if member == interaction.user:
       await interaction.response.send_message(
        "❌ 自分自身は操作できません。",
        ephemeral=True
        )
       return

    if member.top_role >= interaction.user.top_role:
       await interaction.response.send_message(
        "❌ 自分と同等以上のロールは操作できません。",
        ephemeral=True
        )
       return

    if member.top_role >= interaction.guild.me.top_role:
       await interaction.response.send_message(
        "❌ Botより上のロールは操作できません。",
        ephemeral=True
        )
       return


    duration = timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)

    await interaction.response.send_message(
        f"⏳ **{member}** を {minutes}分 タイムアウトしました\n理由: {reason}"
    )

    await send_log(
        interaction.guild,
        f"⏳ TIMEOUT\n実行者: {interaction.user}\n対象: {member}\n理由: {reason}"
    )

LOG_CHANNEL_ID = 1465703396853026973

async def send_log(guild: discord.Guild, message: str):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(message)

@bot.tree.command(name="untimeout", description="メンバーのタイムアウトを解除します")
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
@app_commands.describe(
    member="対象",
    reason="理由"
)
async def untimeout(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "無し"
):
    # 自分自身チェック
    if member == interaction.user:
        await interaction.response.send_message(
            "❌ 自分自身は操作できません。",
            ephemeral=True
        )
        return

    # ロール上下（実行者）
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message(
            "❌ 自分と同等以上のロールは操作できません。",
            ephemeral=True
        )
        return

    # ロール上下（Bot）
    bot_member = interaction.guild.me
    if member.top_role >= bot_member.top_role:
        await interaction.response.send_message(
            "❌ Botより上のロールは操作できません。",
            ephemeral=True
        )
        return

    # タイムアウトされているか確認
    if member.timed_out_until is None:
        await interaction.response.send_message(
            "ℹ️ そのメンバーは現在タイムアウトされていません。",
            ephemeral=True
        )
        return

    # タイムアウト解除
    await member.timeout(None, reason=reason)

    # 実行結果
    await interaction.response.send_message(
        f"🔓 **{member}** のタイムアウトを解除しました\n理由: {reason}"
    )

    # ログ送信
    await send_log(
        interaction.guild,
        f"🔓 UNTIMEOUT\n実行者: {interaction.user}\n対象: {member}\n理由: {reason}"
    )

ITEMS_PER_PAGE = 10

class BanListView(View):
    def __init__(self, bans, author_id):
        super().__init__(timeout=180)
        self.bans = bans
        self.author_id = author_id
        self.page = 0
        self.max_page = (len(bans) - 1) // ITEMS_PER_PAGE

    def get_page_content(self):
        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        chunk = self.bans[start:end]
        content = "\n".join(f"ユーザーID:`{entry.user.id}`\nユーザーネーム:{entry.user}" for entry in chunk)
        content = f"🚫 **BANユーザーID一覧（{len(self.bans)}人）**\n{content}"
        if self.max_page > 0:
            content += f"\n\nページ {self.page + 1}/{self.max_page + 1}"
        return content

    async def update_message(self, interaction):
        content = self.get_page_content()
        await interaction.response.edit_message(content=content, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def prev(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("これはあなた専用のボタンです。", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("これはあなた専用のボタンです。", ephemeral=True)
            return
        if self.page < self.max_page:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()


@bot.tree.command(
    name="banlist",
    description="BANされているユーザーの一覧を表示します。また、IDを指定するとそのユーザーがBANされているか確認することができます。"
)
@app_commands.describe(user_id="BANされているか確認したいユーザーID")
@app_commands.checks.has_permissions(ban_members=True)
async def banlist(interaction: discord.Interaction, user_id: str | None = None):
    bans = [entry async for entry in interaction.guild.bans()]

    # 特定IDチェック
    if user_id:
        for entry in bans:
            if str(entry.user.id) == user_id:
                await interaction.response.send_message(
                    f"🚫 ユーザーID:`{user_id}`\nユーザーネーム:{entry.user} は **BANされています**。",
                    ephemeral=True
                )
                return
        await interaction.response.send_message(
            f"✅ ユーザーID:`{user_id}`\nユーザーネーム:{entry.user} は **BANされていません**。",
            ephemeral=True
        )
        return

    if not bans:
        await interaction.response.send_message(
            "このサーバーにはBANされているユーザーはいません。",
            ephemeral=True
        )
        return

    view = BanListView(bans, interaction.user.id)
    content = view.get_page_content()  # 最初のページを作成して送信
    await interaction.response.send_message(content=content, view=view, ephemeral=True)


@banlist.error
async def banlist_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "このコマンドを使う権限がありません。",
            ephemeral=True
        )

LOG_CHANNEL_ID = 1465702012921581828

class PurgeConfirmView(View):
    def __init__(self, interaction, amount, user):
        super().__init__(timeout=30)
        self.interaction = interaction
        self.amount = amount
        self.user = user
        self.author_id = interaction.user.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "この操作はコマンド実行者のみ行えます。",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="✅ 削除する", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        channel = interaction.channel

        def check(msg: discord.Message):
            if self.user:
                return msg.author.id == self.user.id
            return True

        deleted = await channel.purge(limit=self.amount, check=check)

        # ----- ログ送信 -----
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🧹 メッセージ削除ログ",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="実行者", value=f"{interaction.user} (`{interaction.user.id}`)", inline=False)
            embed.add_field(name="チャンネル", value=channel.mention, inline=False)
            embed.add_field(name="削除数", value=str(len(deleted)), inline=True)
            if self.user:
                embed.add_field(name="対象ユーザー", value=f"{self.user} (`{self.user.id}`)", inline=False)

            await log_channel.send(embed=embed)

        await interaction.response.edit_message(
            content=f"🧹 **{len(deleted)}件** のメッセージを削除しました。",
            view=None
        )

    @discord.ui.button(label="❌ キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content="❌ 削除をキャンセルしました。",
            view=None
        )


# ---------- /purge コマンド ----------
@bot.tree.command(
    name="clear",
    description="メッセージを一括削除します。また、ユーザーを指定するとそのユーザーのメッセージのみ削除することができます。"
)
@app_commands.describe(
    amount="削除するメッセージ数（1〜100）",
    user="特定ユーザーのメッセージのみ削除"
)
@app_commands.checks.has_permissions(administrator=True)
async def purge(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 100],
    user: discord.User | None = None
):
    target_text = f"{user} のメッセージを" if user else ""
    content = (
        f"⚠️ **確認**\n"
        f"{target_text} **{amount}件** 削除します。\n"
        f"本当に削除しますか？"
    )

    view = PurgeConfirmView(interaction, amount, user)
    await interaction.response.send_message(
        content=content,
        view=view,
        ephemeral=True
    )


@purge.error
async def purge_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "このコマンドを使う権限がありません。",
            ephemeral=True
        )

FROM_ROLE_ID = 1469968698730352675
TO_ROLE_ID   = 1469968699082539124

@bot.tree.command(name="verify", description="メンバーを認証済みの状態にします。")
@app_commands.describe(member="認証するメンバー")
async def roleswap(interaction: discord.Interaction, member: discord.Member):

    from_role = interaction.guild.get_role(FROM_ROLE_ID)
    to_role = interaction.guild.get_role(TO_ROLE_ID)

    if from_role is None or to_role is None:
        await interaction.response.send_message(
            "ロールが見つかりません。",
            ephemeral=True
        )
        return

    if from_role not in member.roles:
        await interaction.response.send_message(
            f"対象者は既に認証済みです。",
            ephemeral=True
        )
        return

    try:
        await member.remove_roles(from_role)
        await member.add_roles(to_role)

        await interaction.response.send_message(
            f"認証完了！✅"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "権限が足りません。（Botのロール位置を確認してください）",
            ephemeral=True
        )

fixed_messages = {}

@bot.command()
@commands.has_permissions(manage_messages=True)
async def fix(ctx, *, content: str):
    # 既に固定メッセージがあれば削除
    if ctx.channel.id in fixed_messages:
        try:
            old_msg = await ctx.channel.fetch_message(
                fixed_messages[ctx.channel.id]["message_id"]
            )
            await old_msg.delete()
        except:
            pass

    # 新しく送信
    msg = await ctx.send(content)

    fixed_messages[ctx.channel.id] = {
        "content": content,
        "message_id": msg.id
    }

    await ctx.message.delete()

@bot.event
async def on_message(message):
    # Bot自身 or コマンドは無視
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel_id = message.channel.id

    if channel_id not in fixed_messages:
        return

    data = fixed_messages[channel_id]

    try:
        old_msg = await message.channel.fetch_message(data["message_id"])
        await old_msg.delete()
    except:
        pass

    # 再送信
    new_msg = await message.channel.send(data["content"])
    fixed_messages[channel_id]["message_id"] = new_msg.id

bot.run(os.getenv("TOKEN"))
