import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import io

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
    f"🚫 BAN | 実行者: {interaction.user} | 対象: {member} | 理由: {reason}"
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
        f"👢 KICK | 実行者: {interaction.user} | 対象: {member} | 理由: {reason}"
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
        f"⏳ TIMEOUT | 実行者: {interaction.user} | 対象: {member} | {minutes}分 | 理由: {reason}"
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
        f"🔓 UNTIMEOUT | 実行者: {interaction.user} | 対象: {member} | 理由: {reason}"
    )

@bot.tree.command(
    name="banlist",
    description="BANリストを表示します。また、IDを指定するとそのユーザーがサーバーからBANされているか確認することができます。"
)
@app_commands.describe(
    user_id="BANされているか確認したいユーザーID"
)
@app_commands.checks.has_permissions(ban_members=True)
async def banlist(
    interaction: discord.Interaction,
    user_id: str | None = None
):
    bans = [entry async for entry in interaction.guild.bans()]

    # ---------- 特定IDチェック ----------
    if user_id:
        for entry in bans:
            if str(entry.user.id) == user_id:
                await interaction.response.send_message(
                    f"🚫 ユーザーID `{user_id}` は **BANされています**。",
                    ephemeral=True
                )
                return

        await interaction.response.send_message(
            f"✅ ユーザーID `{user_id}` は **BANされていません**。",
            ephemeral=True
        )
        return

    # ---------- BAN一覧 ----------
    if not bans:
        await interaction.response.send_message(
            "このサーバーにはBANされているユーザーはいません。",
            ephemeral=True
        )
        return

    # txt内容作成（IDのみ）
    text = ""
    for entry in bans:
        text += f"`{entry.user.id}`\n"

    # txtファイル化（メモリ上）
    file = discord.File(
        io.BytesIO(text.encode("utf-8")),
        filename="banlist.txt"
    )

    await interaction.response.send_message(
        content=f"🚫 BANユーザー数：**{len(bans)}**",
        file=file,
        ephemeral=True
    )

@banlist.error
async def banlist_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "このコマンドを使う権限がありません。",
            ephemeral=True
        )


bot.run(os.getenv("TOKEN"))


