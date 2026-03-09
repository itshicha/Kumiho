from keep_alive import keep_alive

keep_alive()
import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import datetime

# --- إعدادات البوت والـ Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(
        name="searching for one piece"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} من أوامر السلاش!")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")
    print(f'✅ {bot.user.name} متصل وجاهز!')


# --- دالة مساعدة لإنشاء Embed سريع ---
def quick_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed


# --- [1] أوامر السلاش (Slash Commands) ---


@bot.tree.command(name="server", description="عرض معلومات السيرفر الحالية")
async def server_slash(interaction: discord.Interaction):
    guild = interaction.guild
    channels_count = len(guild.channels)
    roles_count = len(guild.roles)
    embed = discord.Embed(title=f"🏰 معلومات سيرفر {guild.name}",
                          color=discord.Color.purple(),
                          timestamp=datetime.datetime.now())
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر",
                    value=guild.owner.mention,
                    inline=True)
    embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="👥 عدد الأعضاء",
                    value=f"**{guild.member_count}**",
                    inline=True)
    embed.add_field(name="💬 عدد القنوات",
                    value=f"**{channels_count}**",
                    inline=True)
    embed.add_field(name="🎭 عدد الرتب",
                    value=f"**{roles_count}**",
                    inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء",
                    value=f"**{guild.created_at.strftime('%Y/%m/%d')}**",
                    inline=True)
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}",
                     icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction,
                    member: discord.Member,
                    reason: str = "غير محدد"):
    if member == interaction.user:
        await interaction.response.send_message(embed=quick_embed(
            "❌ خطأ", "ما تقدر تبند نفسك!", discord.Color.red()),
                                                ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(embed=quick_embed(
        "✅ تم الحظر", f"تم حظر {member.mention} بنجاح.", discord.Color.green())
                                            )


@bot.tree.command(name="unban",
                  description="إلغاء الحظر عن عضو باستخدام الـ ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        embed = discord.Embed(title="✅ تم إلغاء الحظر",
                              description=f"تم فك الحظر عن **{user.name}**.",
                              color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(embed=quick_embed(
            "❌ خطأ", f"حدث خطأ: {e}", discord.Color.red()),
                                                ephemeral=True)


@bot.tree.command(name="timeout", description="إسكات عضو لفترة محددة")
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_timeout(interaction: discord.Interaction,
                        member: discord.Member,
                        minutes: int,
                        reason: str = "غير محدد"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(embed=quick_embed(
        "✅ تم الإسكات", f"تم إسكات {member.mention} لمدة {minutes} دقيقة.",
        discord.Color.orange()))


@bot.tree.command(name="untimeout", description="إلغاء الإسكات")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout_slash(interaction: discord.Interaction,
                          member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(embed=quick_embed(
        "✅ تم إلغاء الإسكات", f"تم إلغاء الإسكات عن {member.mention}.",
        discord.Color.green()))


@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def slash_avatar(interaction: discord.Interaction,
                       member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"صورة {member.name}",
                          color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="user", description="عرض معلومات المستخدم")
async def user_slash(interaction: discord.Interaction,
                     member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 معلومات {member.name}",
                          color=discord.Color.blue(),
                          timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="📅 Joined Discord",
                    value=f"**{member.created_at.strftime('%Y/%m/%d')}**",
                    inline=False)
    embed.add_field(name="📥 Joined Server",
                    value=f"**{member.joined_at.strftime('%Y/%m/%d')}**",
                    inline=False)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="🎭 Top Role",
                    value=member.top_role.mention,
                    inline=True)
    await interaction.response.send_message(embed=embed)


# --- [2] نظام الردود التلقائية ---


@bot.event
async def on_message(message):
    if message.author.bot: return
    msg = message.content.strip().lower()
    if msg == "السلام عليكم":
        await message.channel.send(
            embed=quick_embed(None, "وعليكم السلام ورحمة الله وبركاته ❤️"))
    elif msg in ["صباح الخير", "صباح النور"]:
        await message.channel.send(
            embed=quick_embed(None, "صباح النور والسرور! ☀️"))
    elif msg in ["كوميهو", "kumiho"]:
        await message.channel.send(
            embed=quick_embed(None, "آمر نعم، أنا هنا! 🦊"))
    await bot.process_commands(message)


# --- [3] أوامر البريفيكس (Prefix Commands) ---


@bot.command(name="طير")
@commands.has_permissions(ban_members=True)
async def cmd_ban(ctx, member: discord.Member, *, reason="غير محدد"):
    await member.ban(reason=reason)
    await ctx.send(embed=quick_embed("🚀 طيران نهائي",
                                     f"تم طرد {member.mention} من السيرفر!",
                                     discord.Color.red())) 
    
@bot.command(name="اختفي")
@commands.has_permissions(moderate_members=True)
async def cmd_timeout(ctx, member: discord.Member, minutes: int = 10):
    # 1. تنفيذ العقوبة
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration)
    
    # 2. رسالة التأكيد في الشات الحالي
    embed = discord.Embed(
        description=f"🤐 {member.mention} اختفى لمدة {minutes} دقائق.",
        color=discord.Color.orange())
    embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

    # 3. إرسال اللوق (باستخدام محرك البحث المباشر عن القناة)
    log_id = 1479860137970630746
    # نحاول جلب القناة بأكثر من طريقة لضمان الوصول
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    
    if log_channel:
        try:
            log_embed = discord.Embed(
                title="🔨 تنفيذ عقوبة: اختفي",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            log_embed.add_field(name="المشرف:", value=f"{ctx.author.mention}", inline=True)
            log_embed.add_field(name="العضو المعاقب:", value=f"{member.mention}", inline=True)
            log_embed.add_field(name="المدة:", value=f"{minutes} دقيقة", inline=True)
            log_embed.set_footer(text=f"سجل الإدارة | {ctx.author.name}")
            
            await log_channel.send(embed=log_embed)
            print(f"✅ تم إرسال اللوق بنجاح لروم: {log_channel.name}")
        except Exception as e:
            print(f"❌ خطأ تقني في إرسال اللوق: {e}")
    else:
        print(f"⚠️ تنبيه: البوت لم يجد أي قناة بالآيدي {log_id}")

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def cmd_clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(embed=quick_embed("🧹 تنظيف",
                                     f"تم مسح {amount} رسالة بنجاح.",
                                     discord.Color.blue()),
                   delete_after=5)


@bot.command(name="u", aliases=["U"])
async def fast_user_info(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"معلومات {member.name}",
                          color=discord.Color.blue(),
                          timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="📅 Joined Discord :",
                    value=f"**{member.created_at.strftime('%Y/%m/%d')}**",
                    inline=False)
    embed.add_field(name="📥 Joined Server :",
                    value=f"**{member.joined_at.strftime('%Y/%m/%d')}**",
                    inline=False)
    embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="🎭 Top Role",
                    value=member.top_role.mention,
                    inline=True)
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.name}",
                     icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="a", aliases=["A"])
async def short_avatar_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"صورة {member.name}",
                          color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="s", aliases=["S"])
async def fast_server_info(ctx):
    guild = ctx.guild
    channels_count = len(guild.channels)
    roles_count = len(guild.roles)
    embed = discord.Embed(title=f"🏰 معلومات سيرفر {guild.name}",
                          color=discord.Color.purple(),
                          timestamp=datetime.datetime.now())
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر",
                    value=guild.owner.mention,
                    inline=True)
    embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="👥 عدد الأعضاء",
                    value=f"**{guild.member_count}**",
                    inline=True)
    embed.add_field(name="💬 عدد القنوات",
                    value=f"**{channels_count}**",
                    inline=True)
    embed.add_field(name="🎭 عدد الرتب",
                    value=f"**{roles_count}**",
                    inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء",
                    value=f"**{guild.created_at.strftime('%Y/%m/%d')}**",
                    inline=True)
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.name}",
                     icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="قفل")
@commands.has_permissions(manage_channels=True)
async def lock_cmd(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=False)
    await ctx.send(embed=quick_embed("🔒 قفل القناة", "تم قفل القناة بنجاح.",
                                     discord.Color.red()))


@bot.command(name="فتح")
@commands.has_permissions(manage_channels=True)
async def unlock_cmd(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=True)
    await ctx.send(embed=quick_embed("🔓 فتح القناة", "تم فتح القناة، انطلقوا!",
                                     discord.Color.green()))


@bot.command(name="سولف")
@commands.has_permissions(moderate_members=True)
async def cmd_untimeout(ctx, member: discord.Member):
    try:
        # إلغاء التايم آوت (الإسكات)
        await member.timeout(None)

        embed = discord.Embed(
            description=f"✅ أبشر، شلت الإسكات عن {member.mention}.. خله يسولف!",
            color=discord.Color.green())
        # إضافة صورة الشخص اللي انشال عنه التايم آوت
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        await ctx.send(embed=embed)
    except Exception as e:
        # رد في حال حدث خطأ (مثلاً البوت ما عنده صلاحيات كافية)
        await ctx.send(embed=quick_embed("❌ خطأ", f"ما قدرت أشيل الإسكات: {e}",
                                         discord.Color.red()))


# --- [4] معالج الأخطاء ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=quick_embed(
            "⚠️ تنبيه", "ناقص منشن أو معلومات للأمر!", discord.Color.gold()))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=quick_embed("🚫 مرفوض", "ما عندك صلاحيات كافية!",
                                         discord.Color.red()))
# 1. قائمة الكلمات الممنوعة التي حددتها
BANNED_WORDS = ["بكمي", "فيمبوي", "زق", "fuck", "bitch", "مخنث", "يلعن", "ملعون", "قي", "قاي", "gay"]

# 2. أيدي (ID) غرفة اللوق الخاصة بك (تم تحديثه)
LOG_CHANNEL_ID = 1479860456758706257

@bot.event
async def on_message(message):
    # يتجاهل رسائل البوت
    if message.author == bot.user:
        return

    # فحص الكلمات (سيحذف للأونر والجميع)
    msg_content = message.content.lower()
    if any(word in msg_content for word in BANNED_WORDS):
        try:
            # تخزين البيانات قبل الحذف
            author = message.author
            content = message.content
            channel = message.channel

            # الحذف الصامت فوراً
            await message.delete()

            # إرسال التفاصيل لغرفة اللوق (Log) للمشرفين
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🚫 تم رصد كلمة ممنوعة وحذفها", 
                    color=discord.Color.from_rgb(255, 0, 0) # لون أحمر
                )
                embed.add_field(name="المرسل:", value=f"{author.mention} ({author.name})", inline=True)
                embed.add_field(name="القناة:", value=channel.mention, inline=True)
                embed.add_field(name="المحتوى المحذوف:", value=f"```{content}```", inline=False)
                embed.set_footer(text="نظام الحماية التلقائي - كُميهو")
                await log_channel.send(embed=embed)
            
            return # إنهاء المعالجة للرسالة المحذوفة
        except Exception as e:
            # طباعة الخطأ في كونسول ريبليت فقط للتأكد
            print(f"حدث خطأ: {e}")

    # استمرار عمل بقية الأوامر والـ Slash Commands
    await bot.process_commands(message)

BANNED_WORDS = ["طيز", "مكوة", "كسمك", "كس", "زب"]
DELETE_LOG_ID = 1479860456758706257 
TIMEOUT_LOG_ID = 1479860137970630746

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg_content = message.content.lower()
    if any(word in msg_content for word in BANNED_WORDS):
        try:
            author = message.author
            content = message.content
            channel = message.channel

            await message.delete()

            duration = datetime.timedelta(hours=2)
            await author.timeout(duration, reason="كلمات محظورة")

            del_log = bot.get_channel(DELETE_LOG_ID)
            if del_log:
                embed_del = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.dark_gray())
                embed_del.add_field(name="المرسل:", value=author.mention, inline=True)
                embed_del.add_field(name="المحتوى:", value=f"```{content}```", inline=False)
                await del_log.send(embed=embed_del)

            time_log = bot.get_channel(TIMEOUT_LOG_ID)
            if time_log:
                embed_time = discord.Embed(title="🚫 عقوبة تايم أوت", color=discord.Color.red())
                embed_time.add_field(name="المخالف:", value=f"{author.mention}", inline=True)
                embed_time.add_field(name="المدة:", value="ساعتين", inline=True)
                await time_log.send(embed=embed_time)
            
            return
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)
    
bot.run(os.environ['TOKEN'])
