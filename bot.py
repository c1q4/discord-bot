import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord.ui import View, Button
from datetime import datetime
import json
import io
import os
import asyncio
import datetime

# .env から TOKEN を読み込む
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # メッセージを読むために必要

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
     activity = discord.Game(name="discord.gg/roblox-jp")
    await bot.change_presence(status=discord.Status.online, activity=activity)
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

DATA_FILE = "fixed_messages.json"

fixed_messages = {}

def save_data():
    data_to_save = {
        str(channel_id): {
            "content": data["content"],
            "message_id": data["message_id"]
        }
        for channel_id, data in fixed_messages.items()
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)


# -------------------------
# データ読み込み
# -------------------------
async def load_data():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for channel_id_str, info in data.items():
        channel = bot.get_channel(int(channel_id_str))
        if channel is None:
            continue

        try:
            # 起動時に最新化（再送信して一番下へ）
            new_msg = await channel.send(info["content"])

            fixed_messages[int(channel_id_str)] = {
                "content": info["content"],
                "message_id": new_msg.id,
                "lock": asyncio.Lock()
            }

        except:
            pass

    save_data()


# -------------------------
# 起動時
# -------------------------
@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")
    await load_data()


# -------------------------
# !fix
# -------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def fix(ctx, *, content: str):

    # 既存削除
    if ctx.channel.id in fixed_messages:
        try:
            old_msg = await ctx.channel.fetch_message(
                fixed_messages[ctx.channel.id]["message_id"]
            )
            await old_msg.delete()
        except:
            pass

    msg = await ctx.send(content)

    fixed_messages[ctx.channel.id] = {
        "content": content,
        "message_id": msg.id,
        "lock": asyncio.Lock()
    }

    save_data()
    await ctx.message.delete()


# -------------------------
# !unfix
# -------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unfix(ctx):

    if ctx.channel.id not in fixed_messages:
        await ctx.send("❌ 固定メッセージはありません", delete_after=5)
        return

    try:
        old_msg = await ctx.channel.fetch_message(
            fixed_messages[ctx.channel.id]["message_id"]
        )
        await old_msg.delete()
    except:
        pass

    del fixed_messages[ctx.channel.id]
    save_data()

    await ctx.send("✅ 固定を解除しました", delete_after=5)


# -------------------------
# メッセージ監視
# -------------------------
@bot.event
async def on_message(message):

    await bot.process_commands(message)
    
    if message.author.bot:
        return
    
    channel_id = message.channel.id

    if channel_id not in fixed_messages:
        return

    data = fixed_messages[channel_id]

    async with data["lock"]:

        try:
            old_msg = await message.channel.fetch_message(data["message_id"])
            await old_msg.delete()
        except:
            pass

        new_msg = await message.channel.send(data["content"])
        fixed_messages[channel_id]["message_id"] = new_msg.id
        save_data()


TICKET_CATEGORY_ID = 1469968700932362379  # チケットを作るカテゴリID
SUPPORT_ROLE_ID = 1471439011934507071  # サポートスタッフロールID
LOG_CHANNEL_ID = 1471786731006201877
DATA_FILE = "ticket_data.json"

ticket_lock = asyncio.Lock()

# ====== チケット番号管理 ======
def get_next_ticket_number():
    if not os.path.exists(DATA_FILE):
        return 1
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data.get("last_number", 0) + 1

def save_ticket_number(number):
    with open(DATA_FILE, "w") as f:
        json.dump({"last_number": number}, f)

# ====== HTMLログ生成 ======
async def generate_html_log(channel: discord.TextChannel):
    messages = []

    async for msg in channel.history(limit=None, oldest_first=True):
        created = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content = msg.content.replace("<", "&lt;").replace(">", "&gt;")

        attachments = ""
        for attachment in msg.attachments:
            attachments += f'<br><a href="{attachment.url}">{attachment.filename}</a>'

        messages.append(f"""
        <div class="message">
            <span class="author">{msg.author}:</span>
            <span class="time">{created}</span>
            <div class="content">{content}{attachments}</div>
        </div>
        """)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{channel.name} log</title>
        <style>
            body {{ font-family: Arial; background-color: #2c2f33; color: white; }}
            .message {{ margin-bottom: 10px; padding: 5px; }}
            .author {{ font-weight: bold; color: #00b0f4; }}
            .time {{ font-size: 0.8em; color: gray; margin-left: 10px; }}
        </style>
    </head>
    <body>
        <h2>Ticket Log - {channel.name}</h2>
        {''.join(messages)}
    </body>
    </html>
    """

    filename = f"{channel.name}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename

# ====== 閉じる確認 ======
class ConfirmCloseView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="閉じる", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.user:
            await interaction.response.send_message("あなたの操作ではありません", ephemeral=True)
            return

        await interaction.response.send_message("ログを保存しています...", ephemeral=True)

        channel = interaction.channel
        filename = await generate_html_log(channel)

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)

        with open(filename, "rb") as f:
            await log_channel.send(
                content=f"📁チケットログ: {channel.name}",
                file=discord.File(f)
            )

        os.remove(filename)
        await channel.delete()

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.user:
            await interaction.response.send_message("あなたの操作ではありません", ephemeral=True)
            return

        await interaction.response.send_message("キャンセルしました", ephemeral=True)

# ====== 閉じるボタン ======
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="チケットを閉じる",
        style=discord.ButtonStyle.red,
        emoji="🗑️",
        custom_id="close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ConfirmCloseView(interaction.user)
        await interaction.response.send_message(
            "本当にチケットを閉じますか？",
            view=view,
            ephemeral=True
        )

# ====== ドロップダウン ======
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="質問-要望", emoji="🙋🏽"),
            discord.SelectOption(label="規約違反者の報告", emoji="💀"),
            discord.SelectOption(label="認証サポート", emoji="✔️"),
        ]
        super().__init__(
            placeholder="内容を選択してください",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        async with ticket_lock:
            ticket_number = get_next_ticket_number()
            guild = interaction.guild
            category = guild.get_channel(TICKET_CATEGORY_ID)
            support_role = guild.get_role(SUPPORT_ROLE_ID)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            channel = await guild.create_text_channel(
                name=f"ticket-{ticket_number:04}",
                category=category,
                overwrites=overwrites
            )

            selected = self.values[0]

            # Embed作成
            if selected == "🙋🏽質問-要望":
                embed = discord.Embed(
                    title=f"🙋🏽質問-要望 #{ticket_number:04}",
                    description=f"**要件を書いてお待ちください。**\n<&1469968699082539130>\n作成者：{interaction.user.mention}\nUSERNAME：`{interaction.user.name}`",
                    color=0x3498db
                )
            elif selected == "💀規約違反者の報告":
                embed = discord.Embed(
                    title=f"💀規約違反者の報告 #{ticket_number:04}",
                    description=f"**要件を書いてお待ちください。**\n<&1469968699082539130>\n作成者：{interaction.user.mention}\nUSERNAME：`{interaction.user.name}`",
                    color=0xe74c3c
                )
            elif selected == "✔️認証サポート":
                embed = discord.Embed(
                    title=f"✔️認証サポート #{ticket_number:04}",
                    description=f"**要件を書いてお待ちください。**\n<&1469968699082539130>\n作成者：{interaction.user.mention}\nUSERNAME：`{interaction.user.name}`",
                    color=0x2ecc71
                )
            else:
                embed = discord.Embed(
                    title=f"📩 お問い合わせ #{ticket_number:04}",
                    description=f"**要件を書いてお待ちください。**\n<&1469968699082539130>\n作成者：{interaction.user.mention}\nUSERNAME：`{interaction.user.name}`",
                    color=0x95a5a6
                )

            await channel.send(content=interaction.user.mention, embed=embed, view=CloseView())
            save_ticket_number(ticket_number)
            await interaction.response.send_message(f"作成完了：{channel.mention}", ephemeral=True)

# ====== パネル設置 ======
@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):

    embed = discord.Embed(
        title="お問い合わせ一覧",
        description="【🙋質問-要望】\nサーバーへ質問や相談、してほしいことなど要望があればこちらで受け付けます。\nサーバーへ問い合わせる時は基本ここでお願いします。\n\n【💀規約違反者の報告】\n当サーバーの規約に違反しているメンバーがいたら、こちらで報告をお願いします。\n\n【✅認証サポート】\nサーバー入室時の認証がうまくいかない場合、こちらで報告してください。\nまた認証済みの方はこのチケットの作成はやめてください。\n\n問合せカテゴリが確認できましたら、下のボタンを押し問合せ内容を選択してください。",
        color=0x3498db
    )

    await ctx.send(embed=embed, view=TicketView())

# ====== 再起動対応 ======
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseView())

    activity = discord.Game(name="チケット受付中")
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

    print("✅ チケットシステム起動完了")


bot.run(os.getenv("TOKEN"))









