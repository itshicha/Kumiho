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
    await bot.change_presence(activity=discord.Game(name="searching for one piece"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} من أوامر السلاش!")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")
    print(f"✅ {bot.user.name} متصل وجاهز!")


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
    embed = discord.Embed(
        title=f"🏰 معلومات سيرفر {guild.name}",
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now(),
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
    embed.add_field(
        name="👥 عدد الأعضاء", value=f"**{guild.member_count}**", inline=True
    )
    embed.add_field(name="💬 عدد القنوات", value=f"**{channels_count}**", inline=True)
    embed.add_field(name="🎭 عدد الرتب", value=f"**{roles_count}**", inline=True)
    embed.add_field(
        name="📅 تاريخ الإنشاء",
        value=f"**{guild.created_at.strftime('%Y/%m/%d')}**",
        inline=True,
    )
    embed.set_footer(
        text=f"طلب بواسطة: {interaction.user.name}",
        icon_url=interaction.user.display_avatar.url,
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(
    interaction: discord.Interaction, member: discord.Member, reason: str = "غير محدد"
):
    if member == interaction.user:
        await interaction.response.send_message(
            embed=quick_embed("❌ خطأ", "ما تقدر تبند نفسك!", discord.Color.red()),
            ephemeral=True,
        )
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(
        embed=quick_embed(
            "✅ تم الحظر", f"تم حظر {member.mention} بنجاح.", discord.Color.green()
        )
    )


@bot.tree.command(name="unban", description="إلغاء الحظر عن عضو باستخدام الـ ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban_slash(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        embed = discord.Embed(
            title="✅ تم إلغاء الحظر",
            description=f"تم فك الحظر عن **{user.name}**.",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(
            embed=quick_embed("❌ خطأ", f"حدث خطأ: {e}", discord.Color.red()),
            ephemeral=True,
        )


@bot.tree.command(
    name="timeout", description="إسكات عضو لفترة محددة (استخدم m للدقائق و h للساعات)"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def slash_timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    duration_str: str,
    reason: str = "غير محدد",
):
    # تحويل النص (مثلاً 10m أو 2h) إلى مدة زمنية
    minutes = 0
    time_unit = duration_str[-1].lower()  # يأخذ آخر حرف (m أو h)
    time_value = duration_str[:-1]  # يأخذ الرقم

    try:
        if time_unit == "m":
            minutes = int(time_value)
        elif time_unit == "h":
            minutes = int(time_value) * 60
        else:
            # إذا كتب رقم فقط بدون m أو h نعتبرها دقائق تلقائياً
            minutes = int(duration_str)
            duration_str = f"{duration_str}m"
    except ValueError:
        return await interaction.response.send_message(
            "❌ صيغة الوقت غلط! استخدم مثلاً `10m` أو `2h`.", ephemeral=True
        )

    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)

    await interaction.response.send_message(
        embed=quick_embed(
            "✅ تم الإسكات",
            f"تم إسكات {member.mention} لمدة {duration_str}.\n**السبب:** {reason}",
            discord.Color.orange(),
        )
    )


@bot.tree.command(name="untimeout", description="إلغاء الإسكات")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout_slash(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(
        embed=quick_embed(
            "✅ تم إلغاء الإسكات",
            f"تم إلغاء الإسكات عن {member.mention}.",
            discord.Color.green(),
        )
    )


@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def slash_avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"صورة {member.name}", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="user", description="عرض معلومات المستخدم")
async def user_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"👤 معلومات {member.name}",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="📅 Joined Discord",
        value=f"**{member.created_at.strftime('%Y/%m/%d')}**",
        inline=False,
    )
    embed.add_field(
        name="📥 Joined Server",
        value=f"**{member.joined_at.strftime('%Y/%m/%d')}**",
        inline=False,
    )
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="🎭 Top Role", value=member.top_role.mention, inline=True)
    await interaction.response.send_message(embed=embed)


# --- [دالة الإمبد - ضرورية جداً] ---
def quick_embed(title, description, color=0xFFD700):
    return discord.Embed(title=title, description=description, color=color)


# --- [3] أوامر البريفيكس (Prefix Commands) ---

import datetime
from dateutil.relativedelta import (
    relativedelta,
)  # تأكد من وجود هذه المكتبة في requirements.txt


@bot.command(name="طير")
@commands.has_permissions(ban_members=True)
async def cmd_ban(
    ctx, member: discord.Member, duration: str = "0d", *, reason="غير محدد"
):
    # 1. تحليل المدة (مثلاً: 10d أو 1m أو 1y)
    unit = duration[-1].lower()
    try:
        amount = int(duration[:-1])
    except ValueError:
        return await ctx.send("❌ صيغة الوقت غلط! استخدم مثلاً: 10d أو 1m أو 2y")

    now = datetime.datetime.now()
    if unit == "d":
        end_date = now + relativedelta(days=amount)
        duration_text = f"{amount} يوم"
    elif unit == "m":
        end_date = now + relativedelta(months=amount)
        duration_text = f"{amount} شهر"
    elif unit == "y":
        end_date = now + relativedelta(years=amount)
        duration_text = f"{amount} سنة"
    else:
        return await ctx.send(
            "❌ وحدة الوقت غير معروفة! استخدم (d للأيام، m للشهور، y للسنوات)"
        )

    # 2. تنفيذ البان
    await member.ban(reason=f"المدة: {duration_text} | السبب: {reason}")

    # 3. رسالة التأكيد في الشات
    embed = discord.Embed(
        title="🚀 طيران نهائي",
        description=f"تم طرد {member.mention} لمدة **{duration_text}**.",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)

    # --- 4. نظام توزيع اللوق (الأيديات الصحيحة) ---
    SERVER_LOGS = {
        1394284974680838388: 1479859945640820756,  # الأساسي
        1182934425013604362: 1480696940151705741,  # كوميهو
    }

    log_id = SERVER_LOGS.get(ctx.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            log_embed = discord.Embed(
                title="🔨 سجل العقوبات: طيران", color=discord.Color.red(), timestamp=now
            )
            log_embed.add_field(name="المشرف:", value=ctx.author.mention, inline=True)
            log_embed.add_field(
                name="العضو المعاقب:", value=member.mention, inline=True
            )
            log_embed.add_field(name="المدة:", value=duration_text, inline=True)
            log_embed.add_field(
                name="تاريخ الانتهاء التقديري:",
                value=end_date.strftime("%Y/%m/%d"),
                inline=True,
            )
            log_embed.add_field(name="السبب:", value=reason, inline=False)
            log_embed.set_footer(text=f"سجل الإدارة | {ctx.guild.name}")

            await log_channel.send(embed=log_embed)


@bot.command(name="اختفي")
@commands.has_permissions(moderate_members=True)
async def cmd_timeout(ctx, member: discord.Member, time: str = "1h"):
    # 1. تحويل الوقت (ساعة تلقائية إذا لم يحدد، أو يدعم m و h)
    minutes = 0
    time = time.lower()

    try:
        if time.endswith("m"):
            minutes = int(time[:-1])
        elif time.endswith("h"):
            minutes = int(time[:-1]) * 60
        else:
            # إذا كتب رقم فقط بدون m أو h نعتبره دقائق
            minutes = int(time)
            time = f"{time}m"
    except ValueError:
        return await ctx.send("❌ صيغة الوقت غير صحيحة! استخدم مثلاً `10m` أو `2h`.")

    # 2. تنفيذ العقوبة
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration)

    # 3. رسالة التأكيد في الشات الحالي
    embed = discord.Embed(
        description=f"🤐 {member.mention} اختفى لمدة {time}.",
        color=discord.Color.orange(),
    )
    embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

    # --- 3. نظام اللوق الذكي (توزيع الأيديات) ---
    SERVER_LOGS = {
        1320015509749170248: 1394284974680838388,  # سيرفرك الأساسي
        1182934425013604362: 1480697058154512546,  # سيرفر KUMIHO
    }

    # جلب الأيدي الصحيح بناءً على السيرفر الحالي
    log_id = SERVER_LOGS.get(ctx.guild.id)

    if log_id:
        # محرك البحث عن القناة (الجزء اللي سألت عنه)
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

        if log_channel:
            try:
                log_embed = discord.Embed(
                    title="🔨 تنفيذ عقوبة: اختفي",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now(),
                )
                log_embed.add_field(
                    name="المشرف:", value=f"{ctx.author.mention}", inline=True
                )
                log_embed.add_field(
                    name="العضو المعاقب:", value=f"{member.mention}", inline=True
                )
                log_embed.add_field(
                    name="المدة:", value=f"{minutes} دقيقة", inline=True
                )
                log_embed.set_footer(text=f"سجل الإدارة | {ctx.author.name}")

                await log_channel.send(embed=log_embed)
                print(
                    f"✅ تم إرسال اللوق بنجاح لروم: {log_channel.name} في سيرفر {ctx.guild.name}"
                )
            except Exception as e:
                print(f"❌ خطأ تقني في إرسال اللوق: {e}")
    else:
        print(f"⚠️ تنبيه: هذا السيرفر ({ctx.guild.name}) غير مسجل في قائمة اللوق.")


@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def cmd_clear(ctx, amount: int):
    # 1. تنفيذ عملية المسح
    await ctx.channel.purge(limit=amount + 1)

    # 2. رسالة تأكيد مؤقتة
    await ctx.send(
        embed=quick_embed(
            "🧹 تنظيف", f"تم مسح {amount} رسالة بنجاح.", discord.Color.blue()
        ),
        delete_after=5,
    )

    # --- 3. نظام توزيع اللوق بناءً على السيرفر الحالي ---
    SERVER_LOGS = {
        1394284974680838388: 1479860456758706257,  # سيرفرك الأساسي -> يرسل لرومه الخاص
        1182934425013604362: 1480697314057392208,  # سيرفر KUMIHO -> يرسل لرومه الخاص
    }

    # جلب أيدي قناة اللوق الصحيحة
    log_id = SERVER_LOGS.get(ctx.guild.id)

    if log_id:
        # محرك جلب القناة
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

        if log_channel:
            try:
                log_embed = discord.Embed(
                    title="🧹 سجل التنظيف",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now(),
                )
                log_embed.add_field(
                    name="المشرف:", value=ctx.author.mention, inline=True
                )
                log_embed.add_field(
                    name="القناة:", value=ctx.channel.mention, inline=True
                )
                log_embed.add_field(
                    name="العدد المحذوف:", value=f"{amount} رسالة", inline=True
                )
                log_embed.set_footer(text=f"إدارة: {ctx.guild.name}")

                await log_channel.send(embed=log_embed)
            except Exception as e:
                print(f"❌ خطأ في إرسال اللوق: {e}")


@bot.command(name="u", aliases=["U"])
async def fast_user_info(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title=f"معلومات {member.name}",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="📅 Joined Discord :",
        value=f"**{member.created_at.strftime('%Y/%m/%d')}**",
        inline=False,
    )
    embed.add_field(
        name="📥 Joined Server :",
        value=f"**{member.joined_at.strftime('%Y/%m/%d')}**",
        inline=False,
    )
    embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="🎭 Top Role", value=member.top_role.mention, inline=True)
    embed.set_footer(
        text=f"طلب بواسطة: {ctx.author.name}", icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)


@bot.command(name="a", aliases=["A"])
async def short_avatar_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"صورة {member.name}", color=discord.Color.blue())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="s", aliases=["S"])
async def fast_server_info(ctx):
    guild = ctx.guild
    channels_count = len(guild.channels)
    roles_count = len(guild.roles)
    embed = discord.Embed(
        title=f"🏰 معلومات سيرفر {guild.name}",
        color=discord.Color.purple(),
        timestamp=datetime.datetime.now(),
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
    embed.add_field(
        name="👥 عدد الأعضاء", value=f"**{guild.member_count}**", inline=True
    )
    embed.add_field(name="💬 عدد القنوات", value=f"**{channels_count}**", inline=True)
    embed.add_field(name="🎭 عدد الرتب", value=f"**{roles_count}**", inline=True)
    embed.add_field(
        name="📅 تاريخ الإنشاء",
        value=f"**{guild.created_at.strftime('%Y/%m/%d')}**",
        inline=True,
    )
    embed.set_footer(
        text=f"طلب بواسطة: {ctx.author.name}", icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)


@bot.command(name="قفل")
@commands.has_permissions(manage_channels=True)
async def lock_cmd(ctx):
    # 1. تنفيذ القفل
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    # 2. رسالة التأكيد في الشات
    await ctx.send(
        embed=quick_embed("🔒 قفل القناة", "تم قفل القناة بنجاح.", discord.Color.red())
    )

    # --- [إضافة اللوق] ---
    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,  # سيرفرك الأساسي
        1182934425013604362: 1480697749774139453,  # سيرفر كوميهو
    }

    log_id = SERVER_LOGS.get(ctx.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 سجل الإدارة: قفل قناة",
                description=f"قام المشرف {ctx.author.mention} بقفل قناة {ctx.channel.mention}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(),
            )
            log_embed.set_footer(text=f"إدارة {ctx.guild.name}")
            await log_channel.send(embed=log_embed)


@bot.command(name="فتح")
@commands.has_permissions(manage_channels=True)
async def unlock_cmd(ctx):
    # 1. تنفيذ الفتح
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    # 2. رسالة التأكيد في الشات
    await ctx.send(
        embed=quick_embed(
            "🔓 فتح القناة", "تم فتح القناة، انطلقوا!", discord.Color.green()
        )
    )

    # --- [إضافة اللوق] ---
    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,  # سيرفرك الأساسي
        1182934425013604362: 1480697749774139453,  # سيرفر كوميهو
    }

    log_id = SERVER_LOGS.get(ctx.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            log_embed = discord.Embed(
                title="🔓 سجل الإدارة: فتح قناة",
                description=f"قام المشرف {ctx.author.mention} بفتح قناة {ctx.channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now(),
            )
            log_embed.set_footer(text=f"إدارة {ctx.guild.name}")
            await log_channel.send(embed=log_embed)


@bot.command(name="سولف")
@commands.has_permissions(moderate_members=True)
async def cmd_untimeout(ctx, member: discord.Member):
    try:
        # 1. إلغاء التايم آوت (الإسكات)
        await member.timeout(None)

        embed = discord.Embed(
            description=f"✅ أبشر، شلت الإسكات عن {member.mention}.. خله يسولف!",
            color=discord.Color.green(),
        )
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        await ctx.send(embed=embed)

    except Exception as e:
        # هذا الجزء هو اللي كان ناقص وكلفك الخطأ
        await ctx.send(f"❌ ما قدرت أشيل الإسكات، تأكد من صلاحيات البوت. الخطأ: {e}")

        # --- [إضافة اللوق] ---
        SERVER_LOGS = {
            1394284974680838388: 1479860137970630746,  # سيرفرك الأساسي
            1182934425013604362: 1480697058154512546,  # سيرفر كوميهو
        }

        log_id = SERVER_LOGS.get(ctx.guild.id)
        if log_id:
            log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="🔓 إلغاء إسكات (سولف)",
                    description=f"المشرف {ctx.author.mention} سمح لـ {member.mention} بالسوالف.",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(),
                )
                log_embed.set_footer(text=f"إدارة {ctx.guild.name}")
                await log_channel.send(embed=log_embed)
        # ---------------------

    except Exception as e:
        await ctx.send(
            embed=quick_embed(
                "❌ خطأ", f"ما قدرت أشيل الإسكات: {e}", discord.Color.red()
            )
        )


# --- [4] معالج الأخطاء ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            embed=quick_embed(
                "⚠️ تنبيه", "ناقص منشن أو معلومات للأمر!", discord.Color.gold()
            )
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            embed=quick_embed("🚫 مرفوض", "ما عندك صلاحيات كافية!", discord.Color.red())
        )


# 1. قائمة الكلمات الممنوعة التي حددتها
BANNED_WORDS = [
    "بكمي",
    "فيمبوي",
    "زق",
    "fuck",
    "bitch",
    "مخنث",
    "يلعن",
    "ملعون",
    "قي",
    "قاي",
    "gay",
]

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
                    color=discord.Color.from_rgb(255, 0, 0),  # لون أحمر
                )
                embed.add_field(
                    name="المرسل:",
                    value=f"{author.mention} ({author.name})",
                    inline=True,
                )
                embed.add_field(name="القناة:", value=channel.mention, inline=True)
                embed.add_field(
                    name="المحتوى المحذوف:", value=f"```{content}```", inline=False
                )
                embed.set_footer(text="نظام الحماية التلقائي - كُميهو")
                await log_channel.send(embed=embed)

            return  # إنهاء المعالجة للرسالة المحذوفة
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
                embed_del = discord.Embed(
                    title="🗑️ رسالة محذوفة", color=discord.Color.dark_gray()
                )
                embed_del.add_field(name="المرسل:", value=author.mention, inline=True)
                embed_del.add_field(
                    name="المحتوى:", value=f"```{content}```", inline=False
                )
                await del_log.send(embed=embed_del)

            time_log = bot.get_channel(TIMEOUT_LOG_ID)
            if time_log:
                embed_time = discord.Embed(
                    title="🚫 عقوبة تايم أوت", color=discord.Color.red()
                )
                embed_time.add_field(
                    name="المخالف:", value=f"{author.mention}", inline=True
                )
                embed_time.add_field(name="المدة:", value="ساعتين", inline=True)
                await time_log.send(embed=embed_time)

            return
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)


# أيدي قناة اللوق الجديدة
MOVE_LOG_CHANNEL_ID = 1479861318331793410


# --- [1] أمر نقل الأعضاء (Move) ---
@bot.tree.command(name="move", description="نقل عضو من قناة صوتية إلى أخرى")
@app_commands.checks.has_permissions(move_members=True)
async def move(
    interaction: discord.Interaction,
    member: discord.Member,
    channel: discord.VoiceChannel,
):
    if not member.voice:
        return await interaction.response.send_message(
            f"❌ {member.mention} ليس متواجداً في قناة صوتية حالياً.", ephemeral=True
        )

        old_channel = member.voice.channel

        try:
            await member.move_to(channel)
            await interaction.response.send_message(
                f"✅ تم نقل {member.mention} إلى **{channel.name}**.", ephemeral=True
            )

            # --- توزيع اللوق الذكي للأمر ---
            SERVER_VOICE_LOGS = {
                1394284974680838388: 1479861318331793410,  # سيرفرك الأساسي
                1182934425013604362: 1480697888257609778,  # سيرفر كوميهو
            }

            log_id = SERVER_VOICE_LOGS.get(interaction.guild.id)
            if log_id:
                log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
                if log_channel:
                    embed = discord.Embed(
                        title="🔄 سجل النقل اليدوي (بواسطة مشرف)",
                        color=discord.Color.blue(),
                        timestamp=datetime.datetime.now(),
                    )
                    embed.add_field(
                        name="بواسطة:", value=interaction.user.mention, inline=True
                    )
                    embed.add_field(
                        name="العضو المنقول:", value=member.mention, inline=True
                    )
                    embed.add_field(name="من:", value=old_channel.name, inline=True)
                    embed.add_field(name="إلى:", value=channel.name, inline=True)
                    embed.set_footer(text=f"إدارة {interaction.guild.name}")
                    await log_channel.send(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ فشل النقل: {e}", ephemeral=True
            )


# --- [لوق الرسائل المعرّب] ---


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    SERVER_MSG_LOGS = {
        1394284974680838388: 1479860456758706257,  # الأساسي
        1182934425013604362: 1480697314057392208,  # كوميهو
    }

    log_id = SERVER_MSG_LOGS.get(message.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            embed = discord.Embed(
                description=f"🗑️ **الرسالة المرسلة من {message.author.mention} تم حذفها في {message.channel.mention}**",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_author(
                name=message.author.name, icon_url=message.author.display_avatar.url
            )
            embed.add_field(
                name="المحتوى",
                value=f"```\n{message.content or 'لا يوجد محتوى نصي'}\n```",
                inline=False,
            )
            embed.set_footer(
                text=f"سيرفر: {message.guild.name} | معرف المستخدم: {message.author.id}"
            )

            await log_channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return

    SERVER_MSG_LOGS = {
        1394284974680838388: 1479860456758706257,  # الأساسي
        1182934425013604362: 1480697314057392208,  # كوميهو
    }

    log_id = SERVER_MSG_LOGS.get(before.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            jump_url = f"[انتقل للرسالة]({after.jump_url})"

            embed = discord.Embed(
                description=f"✏️ **الرسالة المرسلة من {before.author.mention} تم تعديلها في {before.channel.mention}. {jump_url}**",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_author(
                name=before.author.name, icon_url=before.author.display_avatar.url
            )

            # عرض "قبل" و "بعد" بالعربي وبصناديق كود
            embed.add_field(
                name="قبل التعديل", value=f"```\n{before.content}\n```", inline=False
            )
            embed.add_field(
                name="بعد التعديل", value=f"```\n{after.content}\n```", inline=False
            )

            embed.set_footer(
                text=f"سيرفر: {before.guild.name} | معرف المستخدم: {before.author.id}"
            )

            await log_channel.send(embed=embed)


# --- [نظام مراقبة الرومات مع ذكر اسم المشرف] ---


@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.VoiceChannel):
        return

    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697749774139453,
    }

    log_id = SERVER_LOGS.get(channel.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            # البحث في سجل التدقيق عن آخر عملية إنشاء قناة
            entry = None
            async for e in channel.guild.audit_logs(
                action=discord.AuditLogAction.channel_create, limit=1
            ):
                entry = e
                break

            user_name = entry.user.mention if entry else "غير معروف"

            embed = discord.Embed(
                title="🆕 إنشاء قناة جديدة",
                description=f"قام {user_name} بإنشاء قناة كتابية: {channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text=f"إدارة القنوات | {channel.guild.name}")
            await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    if isinstance(channel, discord.VoiceChannel):
        return

    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697749774139453,
    }

    log_id = SERVER_LOGS.get(channel.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            # البحث في سجل التدقيق عن آخر عملية حذف قناة
            entry = None
            async for e in channel.guild.audit_logs(
                action=discord.AuditLogAction.channel_delete, limit=1
            ):
                entry = e
                break

            user_name = entry.user.mention if entry else "غير معروف"

            embed = discord.Embed(
                title="🗑️ حذف قناة",
                description=f"قام {user_name} بحذف قناة: **{channel.name}**",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text=f"إدارة القنوات | {channel.guild.name}")
            await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_update(before, after):
    if isinstance(after, discord.VoiceChannel):
        return

    if before.name != after.name:
        SERVER_LOGS = {
            1394284974680838388: 1479861118137794684,
            1182934425013604362: 1480697749774139453,
        }

        log_id = SERVER_LOGS.get(after.guild.id)
        if log_id:
            log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
            if log_channel:
                # البحث في سجل التدقيق عن آخر عملية تعديل قناة
                entry = None
                async for e in after.guild.audit_logs(
                    action=discord.AuditLogAction.channel_update, limit=1
                ):
                    entry = e
                    break

                user_name = entry.user.mention if entry else "غير معروف"

                embed = discord.Embed(
                    title="📝 تعديل اسم قناة",
                    description=f"قام {user_name} بتعديل اسم القناة {after.mention}",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now(),
                )
                embed.add_field(name="الاسم القديم:", value=before.name, inline=True)
                embed.add_field(name="الاسم الجديد:", value=after.name, inline=True)
                embed.set_footer(text=f"إدارة القنوات | {after.guild.name}")
                await log_channel.send(embed=embed)

    # --- [نظام لوق الرتب المحدث بالأيديات الجديدة] ---


@bot.event
async def on_guild_role_create(role):
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861495373500507,  # الأساسي
        1182934425013604362: 1480697982671388845,  # كوميهو
    }

    log_id = SERVER_ROLE_LOGS.get(role.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            entry = None
            async for e in role.guild.audit_logs(
                action=discord.AuditLogAction.role_create, limit=1
            ):
                entry = e
                break
            user_name = entry.user.mention if entry else "غير معروف"

            embed = discord.Embed(
                title="✨ إنشاء رتبة جديدة",
                description=f"قام {user_name} بإنشاء رتبة: {role.mention}",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text=f"إدارة الرتب | {role.guild.name}")
            await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_delete(role):
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861495373500507,
        1182934425013604362: 1480697982671388845,
    }

    log_id = SERVER_ROLE_LOGS.get(role.guild.id)
    if log_id:
        log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
        if log_channel:
            entry = None
            async for e in role.guild.audit_logs(
                action=discord.AuditLogAction.role_delete, limit=1
            ):
                entry = e
                break
            user_name = entry.user.mention if entry else "غير معروف"

            embed = discord.Embed(
                title="🗑️ حذف رتبة",
                description=f"قام {user_name} بحذف رتبة: **{role.name}**",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text=f"إدارة الرتب | {role.guild.name}")
            await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_update(before, after):
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861495373500507,
        1182934425013604362: 1480697982671388845,
    }

    log_id = SERVER_ROLE_LOGS.get(after.guild.id)
    if not log_id:
        return

    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    if not log_channel:
        return

    entry = None
    async for e in after.guild.audit_logs(
        action=discord.AuditLogAction.role_update, limit=1
    ):
        entry = e
        break
    user_name = entry.user.mention if entry else "غير معروف"

    # 1. حالة تغيير اسم الرتبة
    if before.name != after.name:
        embed = discord.Embed(
            title="📝 تغيير اسم رتبة",
            description=f"قام {user_name} بتعديل اسم رتبة {after.mention}\n**من:** {before.name}\n**إلى:** {after.name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(text=f"تعديل رتبة | {after.guild.name}")
        await log_channel.send(embed=embed)

    # 2. حالة تعديل الصلاحيات (Permissions)
    elif before.permissions != after.permissions:
        embed = discord.Embed(
            title="🛠️ تعديل صلاحيات رتبة",
            description=f"قام {user_name} بتعديل صلاحيات رتبة {after.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(),
        )

        added_perms = [
            p[0]
            for p in after.permissions
            if p[1] and not getattr(before.permissions, p[0])
        ]
        removed_perms = [
            p[0]
            for p in before.permissions
            if p[1] and not getattr(after.permissions, p[0])
        ]

        if added_perms:
            embed.add_field(
                name="✅ صلاحيات أُضيفت:",
                value=", ".join(added_perms).replace("_", " "),
                inline=False,
            )
        if removed_perms:
            embed.add_field(
                name="❌ صلاحيات أُزيلت:",
                value=", ".join(removed_perms).replace("_", " "),
                inline=False,
            )

        embed.set_footer(text=f"تعديل صلاحيات | {after.guild.name}")
        await log_channel.send(embed=embed)


@bot.event
async def on_ready():
    # تحميل الدعوات الحالية لكل سيرفر عند تشغيل البوت
    for guild in bot.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except:
            invites[guild.id] = []
    print("✅ نظام تتبع الداعي جاهز")


@bot.event
async def on_member_join(member):
    # إعدادات رومات اللوق للسيرفرين
    SERVER_INVITE_LOGS = {
        1394284974680838388: 1479860973841027153,  # سيرفرك الأساسي
        1182934425013604362: 1480697579929862184,  # سيرفر كوميهو
    }

    log_id = SERVER_INVITE_LOGS.get(member.guild.id)
    if not log_id:
        return

    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    inviter_mention = "شخص غير معروف"
    total_invites = 0

    try:
        # مقارنة الدعوات القديمة بالجديدة لمعرفة الرابط المستخدم
        invites_before = invites.get(member.guild.id, [])
        invites_after = await member.guild.invites()

        for old_inv in invites_before:
            for new_inv in invites_after:
                if old_inv.code == new_inv.code and old_inv.uses < new_inv.uses:
                    inviter_mention = old_inv.inviter.mention
                    # حساب مجموع دعوات الشخص من كل روابطه
                    total_invites = sum(
                        i.uses
                        for i in invites_after
                        if i.inviter.id == old_inv.inviter.id
                    )
                    break

        # تحديث قائمة الدعوات في الذاكرة
        invites[member.guild.id] = invites_after
    except:
        pass

    if log_channel:
        # نفس صيغة الصورة اللي طلبتها
        msg = f"👤 {member.mention} **just joined.** They were invited by **{inviter_mention}** who now has **{total_invites} invites!**"
        await log_channel.send(msg)


@bot.event
async def on_guild_channel_update(before, after):
    # نراقب فقط القنوات الصوتية
    if not isinstance(after, discord.VoiceChannel):
        return

    # توزيع اللوق للسيرفرين (استخدام الأيديات اللي حددتها)
    SERVER_VOICE_LOGS = {
        1394284974680838388: 147986131833179341,  # سيرفرك الأساسي
        1182934425013604362: 1480697888257609778,  # سيرفر كوميهو
    }

    log_id = SERVER_VOICE_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    # التحقق من نوع التغيير (اسم أو صلاحيات)
    embed = discord.Embed(color=0x2B2D31, timestamp=datetime.datetime.now())
    embed.set_footer(
        text=f"{after.guild.name} | Today at {datetime.datetime.now().strftime('%I:%M %p')}"
    )

    found_change = False

    # 1. حالة تغيير اسم القناة
    if before.name != after.name:
        found_change = True
        responsible_mod = "غير معروف"
        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.channel_update, limit=1
        ):
            if entry.target.id == after.id:
                responsible_mod = entry.user.mention
                break

        embed.title = f"📝 Channel Name Updated: {after.name}"
        embed.add_field(
            name="Old Name:", value=f"```\n{before.name}\n```", inline=False
        )
        embed.add_field(name="New Name:", value=f"```\n{after.name}\n```", inline=False)
        embed.add_field(
            name="Responsible Moderator:", value=responsible_mod, inline=False
        )

    # 2. حالة تغيير الصلاحيات (Permissions) مثل قفل الروم أو فتحه
    elif before.overwrites != after.overwrites:
        found_change = True
        responsible_mod = "غير معروف"
        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.overwrite_update, limit=1
        ):
            if entry.target.id == after.id:
                responsible_mod = entry.user.mention
                break

        embed.title = f"🏠 Channel Permissions Updated: {after.name}"

        # تحديد الصلاحية المتغيرة (مثل الاتصال Connect)
        perm_details = "Permissions details updated"
        for target, overwrite in after.overwrites.items():
            old_overwrite = before.overwrites.get(target)
            if old_overwrite != overwrite:
                target_mention = (
                    target.mention if hasattr(target, "mention") else f"@{target.name}"
                )
                # مثال لصلاحية Connect (⛔ للقفل و ✅ للفتح)
                status = "⛔ Connect" if overwrite.connect == False else "✅ Connect"
                perm_details = f"↘️ **{target_mention}**\n{status}"
                break

        embed.add_field(name="Permissions:", value=perm_details, inline=False)
        embed.add_field(
            name="Responsible Moderator:", value=responsible_mod, inline=False
        )
    # إرسال اللوق إذا وجد تغيير
    if found_change and log_channel:
        await log_channel.send(embed=embed)


# --- [نظام مراقبة إضافة/إزالة وتعديل صلاحيات الأشخاص] ---


@bot.event
async def on_guild_channel_update(before, after):
    # نراقب فقط القنوات الصوتية لتقليل الضغط
    if not isinstance(after, discord.VoiceChannel):
        return

    # التأكد من وجود تغيير في الصلاحيات
    if before.overwrites == after.overwrites:
        return

    # توزيع اللوق للسيرفرين
    SERVER_USER_PERM_LOGS = {
        1394284974680838388: 147986131833179341,  # الأساسي
        1182934425013604362: 1480697888257609778,  # كوميهو
    }

    log_id = SERVER_USER_PERM_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    # جلب المشرف المسؤول من الـ Audit Logs
    responsible_mod = "غير معروف"
    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.overwrite_update, limit=1
    ):
        if entry.target.id == after.id:
            responsible_mod = entry.user.mention
            break

    embed = discord.Embed(color=0x2B2D31, timestamp=datetime.datetime.now())
    embed.set_footer(
        text=f"{after.guild.name} | Today at {datetime.datetime.now().strftime('%I:%M %p')}"
    )

    found_member_change = False

    # 1. فحص الإضافة أو التعديل
    for target, overwrite in after.overwrites.items():
        if isinstance(target, discord.Member):
            old_ov = before.overwrites.get(target)

            # حالة إضافة شخص جديد للروم
            if old_ov is None:
                embed.title = "👤 Member Added to Channel"
                embed.description = (
                    f"تم إضافة **{target.mention}** إلى صلاحيات القناة: {after.mention}"
                )
                found_member_change = True

            # حالة تعديل صلاحيات شخص موجود
            elif old_ov != overwrite:
                embed.title = "⚙️ Member Permissions Updated"
                # تحديد حالة الاتصال (Connect) كمثال
                status = "⛔ Connect" if overwrite.connect == False else "✅ Connect"
                embed.description = f"تم تعديل صلاحيات **{target.mention}** في {after.mention}\n\n↘️ **Permissions:**\n{status}"
                found_member_change = True

            if found_member_change:
                break

    # 2. فحص الإزالة (إذا لم نجد إضافة أو تعديل)
    if not found_member_change:
        for target, old_ov in before.overwrites.items():
            if isinstance(target, discord.Member) and target not in after.overwrites:
                embed.title = "❌ Member Removed from Channel"
                embed.description = (
                    f"تم إزالة **{target.mention}** من صلاحيات القناة: {after.mention}"
                )
                found_member_change = True
                break

    if found_member_change and log_channel:
        embed.add_field(
            name="Responsible Moderator:", value=responsible_mod, inline=False
        )
        await log_channel.send(embed=embed)


# --- [نظام لوق عمليات بوت TempVoice] ---


@bot.event
async def on_guild_channel_update(before, after):
    # نراقب فقط القنوات الصوتية
    if not isinstance(after, discord.VoiceChannel):
        return

    # التأكد من وجود تغيير في الصلاحيات
    if before.overwrites == after.overwrites:
        return

    # توزيع اللوق للسيرفرين (الأيديات اللي حددتها)
    SERVER_TEMP_LOGS = {
        1394284974680838388: 147986131833179341,  # الأساسي
        1182934425013604362: 1480697888257609778,  # كوميهو
    }

    log_id = SERVER_TEMP_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    # جلب المسؤول من الـ Audit Logs للتأكد أنه بوت TempVoice أو مشرف
    responsible_mod = "غير معروف"
    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.overwrite_update, limit=1
    ):
        if entry.target.id == after.id:
            responsible_mod = entry.user
            break

    # إنشاء الـ Embed
    embed = discord.Embed(color=0x2B2D31, timestamp=datetime.datetime.now())
    embed.set_footer(
        text=f"{after.guild.name} | Today at {datetime.datetime.now().strftime('%I:%M %p')}"
    )

    # تحديد الإجراء بناءً على التغيير في صلاحيات @everyone
    ov_before = before.overwrites_for(after.guild.default_role)
    ov_after = after.overwrites_for(after.guild.default_role)

    action_name = "Channel Settings Updated"
    status_text = "Permissions Modified"

    # كشف الخيارات (Lock, Unlock, Invisible, Visible, Chat)
    if ov_before.connect != ov_after.connect:
        action_name = "🔓 Channel Unlocked" if ov_after.connect else "🔒 Channel Locked"
        status_text = (
            "Everyone can join" if ov_after.connect else "Only trusted users can join"
        )

    elif ov_before.view_channel != ov_after.view_channel:
        action_name = (
            "👁️ Channel Visible" if ov_after.view_channel else "🚫 Channel Invisible"
        )
        status_text = (
            "Everyone can view"
            if ov_after.view_channel
            else "Only trusted users can view"
        )

    elif ov_before.send_messages != ov_after.send_messages:
        action_name = "🗨️ Chat Opened" if ov_after.send_messages else "🚫 Chat Closed"
        status_text = (
            "Everyone can text"
            if ov_after.send_messages
            else "Only trusted users can text"
        )

    embed.title = action_name
    embed.description = f"**Channel:** {after.mention}\n**Status:** {status_text}"
    embed.add_field(
        name="Responsible Moderator:", value=responsible_mod.mention, inline=False
    )

    if log_channel:
        await log_channel.send(embed=embed)


import discord
from discord.ext import commands, tasks
from easy_pil import Editor, load_image_async, Font, Canvas
import json
import os

# --- [1] إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# إعدادات الروم والرتب
LEVEL_UP_CHANNEL_ID = 1482373680922103868
ROLES_REWARDS = {
    5: 1243601736057229495,
    15: 1243601881373212672,
    25: 1243601938537250896,
    35: 1243602000415817799,
    45: 1243602062151778446,
    55: 1243602144058277929,
    65: 1482375085498040451,
}


# --- [2] إدارة البيانات ---
def load_levels():
    if os.path.exists("levels.json"):
        with open("levels.json", "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}


def save_levels(data):
    with open("levels.json", "w") as f:
        json.dump(data, f, indent=4)


async def update_member_roles(member, current_level):
    roles_to_add = []
    for lvl_req, role_id in ROLES_REWARDS.items():
        if current_level >= lvl_req:
            role = member.guild.get_role(role_id)
            if role and role not in member.roles:
                roles_to_add.append(role)
    if roles_to_add:
        try:
            await member.add_roles(*roles_to_add)
            return [r.name for r in roles_to_add]
        except:
            return None
    return []


# --- [3] نظام الـ XP والترقية ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    levels = load_levels()
    g_id, u_id = str(message.guild.id), str(message.author.id)
    if g_id not in levels:
        levels[g_id] = {}
    if u_id not in levels[g_id]:
        levels[g_id][u_id] = {"xp": 0, "voice_xp": 0, "level": 1}

    levels[g_id][u_id]["xp"] += 5

    stats = levels[g_id][u_id]
    total_xp = stats["xp"] + stats.get("voice_xp", 0)
    needed_xp = stats["level"] * 200

    if total_xp >= needed_xp:
        stats["level"] += 1
        channel = bot.get_channel(LEVEL_UP_CHANNEL_ID)
        msg = f"🎊 مبروك {message.author.mention}! ارتقيت للمستوى **{stats['level']}**"
        if channel:
            await channel.send(msg)
        added_roles = await update_member_roles(message.author, stats["level"])
        if added_roles and channel:
            await channel.send(f"🎖️ كفو! حصلت على رتبة: **{', '.join(added_roles)}**")

    save_levels(levels)
    await bot.process_commands(message)


@tasks.loop(minutes=1)
async def voice_xp_handler():
    levels = load_levels()
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if member.bot or member.voice.self_deaf:
                    continue
                g_id, u_id = str(guild.id), str(member.id)
                if g_id not in levels:
                    levels[g_id] = {}
                if u_id not in levels[g_id]:
                    levels[g_id][u_id] = {"xp": 0, "voice_xp": 0, "level": 1}
                levels[g_id][u_id]["voice_xp"] = (
                    levels[g_id][u_id].get("voice_xp", 0) + 10
                )
    save_levels(levels)


# --- [4] أمر الرانك بالصور ---
@bot.command(name="rank")
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    levels = load_levels()
    stats = levels.get(str(ctx.guild.id), {}).get(
        str(member.id), {"xp": 0, "voice_xp": 0, "level": 1}
    )

    lvl = stats["level"]
    chat_xp, voice_xp = stats["xp"], stats.get("voice_xp", 0)
    needed_xp = lvl * 200

    try:
        background = Editor("rank_bg.png").resize((900, 450))
    except:
        background = Editor(Canvas((900, 450), color="#1a1a1a"))

    profile_img = await load_image_async(str(member.display_avatar.url))
    profile = Editor(profile_img).resize((180, 180)).circle_image()
    background.paste(profile, (50, 50))

    font_l = Font.poppins(size=45, variant="bold")
    font_s = Font.poppins(size=25, variant="light")

    background.text((280, 70), f"{member.name}", font=font_l, color="#FFFFFF")
    background.text((280, 130), f"LEVEL: {lvl}", font=font_s, color="#ffad14")

    background.bar(
        (280, 210),
        max_width=550,
        height=35,
        percentage=(chat_xp / needed_xp) * 100,
        fill="#ffad14",
    )
    background.text(
        (280, 180), f"CHAT XP: {chat_xp}/{needed_xp}", font=font_s, color="#FFFFFF"
    )

    background.bar(
        (280, 310),
        max_width=550,
        height=35,
        percentage=(voice_xp / needed_xp) * 100,
        fill="#e67e22",
    )
    background.text(
        (280, 280), f"VOICE XP: {voice_xp}/{needed_xp}", font=font_s, color="#FFFFFF"
    )

    file = discord.File(fp=background.image_bytes, filename="rank.png")
    await ctx.send(file=file)


# --- [5] أوامر المتصدرين (تعديل: عرض الكتابي والصوتي معاً) ---
@bot.group(name="top", invoke_without_command=True)
async def top(ctx):
    levels = load_levels()
    g_id = str(ctx.guild.id)
    if g_id not in levels or not levels[g_id]:
        return await ctx.send("القائمة فارغة.")

    # جلب أفضل 10 كتابي
    sorted_text = sorted(
        levels[g_id].items(), key=lambda x: x[1].get("xp", 0), reverse=True
    )[:10]
    text_desc = ""
    for i, (uid, data) in enumerate(sorted_text):
        text_desc += f"**#{i + 1}** | <@{uid}> - `{data.get('xp', 0)}` XP\n"

    # جلب أفضل 10 صوتي
    sorted_voice = sorted(
        levels[g_id].items(), key=lambda x: x[1].get("voice_xp", 0), reverse=True
    )[:10]
    voice_desc = ""
    for i, (uid, data) in enumerate(sorted_voice):
        voice_desc += f"**#{i + 1}** | <@{uid}> - `{data.get('voice_xp', 0)}` XP\n"

    embed = discord.Embed(title="🏆 متصدري السيرفر", color=0xF1C40F)
    embed.add_field(
        name="💬 أفضل 10 كتابي", value=text_desc or "لا توجد بيانات", inline=True
    )
    embed.add_field(
        name="🎙️ أفضل 10 صوتي", value=voice_desc or "لا توجد بيانات", inline=True
    )
    embed.set_footer(
        text=f"طلب بواسطة {ctx.author.name}", icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)


@top.command(name="text")
async def top_text(ctx):
    levels = load_levels()
    g_id = str(ctx.guild.id)
    if g_id not in levels:
        return await ctx.send("لا توجد بيانات.")

    sorted_users = sorted(levels[g_id].items(), key=lambda x: x[1]["xp"], reverse=True)
    desc = ""
    for i, (uid, data) in enumerate(sorted_users[:10]):
        desc += f"**#{i + 1}** | <@{uid}> - Text XP: `{data['xp']}`\n"

    await ctx.send(
        embed=discord.Embed(title="💬 متصدري الكتابة", description=desc, color=0x3498DB)
    )


@top.command(name="voice")
async def top_voice(ctx):
    levels = load_levels()
    g_id = str(ctx.guild.id)
    if g_id not in levels:
        return await ctx.send("لا توجد بيانات.")

    sorted_users = sorted(
        levels[g_id].items(), key=lambda x: x[1].get("voice_xp", 0), reverse=True
    )
    desc = ""
    for i, (uid, data) in enumerate(sorted_users[:10]):
        desc += f"**#{i + 1}** | <@{uid}> - Voice XP: `{data.get('voice_xp', 0)}`\n"

    await ctx.send(
        embed=discord.Embed(title="🎙️ متصدري الفويس", description=desc, color=0x2ECC71)
    )


# --- [6] أوامر الإدارة ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setlevel(ctx, member: discord.Member, level: int):
    levels = load_levels()
    g_id, u_id = str(ctx.guild.id), str(member.id)
    if g_id not in levels:
        levels[g_id] = {}
    levels[g_id][u_id] = {"xp": 0, "voice_xp": 0, "level": level}
    save_levels(levels)
    added = await update_member_roles(member, level)
    msg = f"✅ تم تحديد مستوى {member.mention} بـ **{level}**"
    if added:
        msg += f" ومنحه رتب: {', '.join(added)}"
    await ctx.send(msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def resetxp(ctx, member: discord.Member):
    levels = load_levels()
    if str(ctx.guild.id) in levels and str(member.id) in levels[str(ctx.guild.id)]:
        del levels[str(ctx.guild.id)][str(member.id)]
        save_levels(levels)
        await ctx.send(f"🧹 تم تصفير بيانات {member.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def setxp(ctx, member: discord.Member, amount: int):
    # تحميل البيانات (تأكد أن اسم الدالة مطابق لما عندك)
    levels = load_levels()
    g_id = str(ctx.guild.id)
    u_id = str(member.id)

    if g_id not in levels:
        levels[g_id] = {}

    if u_id not in levels[g_id]:
        levels[g_id][u_id] = {"xp": 0, "level": 1}

    # تحديث الـ XP
    old_xp = levels[g_id][u_id].get("xp", 0)
    levels[g_id][u_id]["xp"] = amount

    # حسبة المستوى الجديد (هنا الحسبة: كل 500 XP ليفل)
    # غير الرقم 500 حسب النظام اللي تمشي عليه في كود setlevel
    new_level = (amount // 500) + 1
    levels[g_id][u_id]["level"] = new_level

    save_levels(levels)

    embed = discord.Embed(
        title="📊 تعديل نقاط الخبرة (XP)",
        description=f"تم تحديث بيانات {member.mention} بنجاح.",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(),
    )
    embed.add_field(name="الـ XP السابق:", value=f"`{old_xp}`", inline=True)
    embed.add_field(name="الـ XP الجديد:", value=f"`{amount}`", inline=True)
    embed.add_field(name="المستوى الحالي:", value=f"⭐ `{new_level}`", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {ctx.author.name}")

    await ctx.send(embed=embed)


@setxp.error
async def setxp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ هذا الأمر للمسؤولين فقط!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "⚠️ خطأ في المدخلات: تأكد من منشن العضو ثم كتابة الرقم (مثال: `!setxp @user 5000`)"
        )


# --- [7] التشغيل ---
@bot.event
async def on_ready():
    if not voice_xp_handler.is_running():
        voice_xp_handler.start()
    print(f"✅ تم التشغيل: {bot.user}")


@bot.event
async def on_member_update(before, after):
    # إعدادات رومات اللوق للسيرفرين
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861495373500507,  # الأساسي
        1182934425013604362: 1480697982671388845,  # كوميهو
    }

    log_id = SERVER_ROLE_LOGS.get(before.guild.id)
    if not log_id:
        return

    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    if not log_channel:
        return

    # التحقق من إضافة رتبة جديدة
    if len(before.roles) < len(after.roles):
        # معرفة الرتبة التي أُضيفت
        new_role = next(role for role in after.roles if role not in before.roles)

        # البحث عن المسؤول في سجل التدقيق
        responsible_mod = "غير معروف"
        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.member_role_update, limit=1
        ):
            if entry.target.id == after.id:
                responsible_mod = entry.user.mention
                break

        embed = discord.Embed(
            title="🛡️ تحديث رتب عضو",
            description=f"**تم إضافة رتبة جديدة لـ {after.mention}**",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_author(name=after.name, icon_url=after.display_avatar.url)
        embed.add_field(name="الرتبة المضافة:", value=new_role.mention, inline=False)
        embed.add_field(name="بواسطة:", value=responsible_mod, inline=False)
        embed.set_footer(text=f"إدارة الرتب | {after.guild.name}")

        await log_channel.send(embed=embed)

    # التحقق من إزالة رتبة
    elif len(before.roles) > len(after.roles):
        removed_role = next(role for role in before.roles if role not in after.roles)

        responsible_mod = "غير معروف"
        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.member_role_update, limit=1
        ):
            if entry.target.id == after.id:
                responsible_mod = entry.user.mention
                break

        embed = discord.Embed(
            title="🛡️ تحديث رتب عضو",
            description=f"**تم إزالة رتبة من {after.mention}**",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_author(name=after.name, icon_url=after.display_avatar.url)
        embed.add_field(
            name="الرتبة التي أُزيلت:", value=removed_role.mention, inline=False
        )
        embed.add_field(name="بواسطة:", value=responsible_mod, inline=False)
        embed.set_footer(text=f"إدارة الرتب | {after.guild.name}")

        await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_update(before, after):
    # إعدادات رومات اللوق للسيرفرين
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861495373500507,
        1182934425013604362: 1480697982671388845,
    }
    log_id = SERVER_ROLE_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    if not log_channel:
        return

    # جلب آخر عملية تعديل رتبة من الـ Audit Log
    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.role_update, limit=1
    ):
        if entry.target.id == after.id:
            responsible_mod = entry.user.mention

            embed = discord.Embed(
                title="⚙️ تعديل في إعدادات الرتبة",
                description=f"تم التعديل على رتبة: {after.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(),
            )

            # 1. فحص تغير الصلاحيات (Permissions)
            if before.permissions != after.permissions:
                added_perms = [
                    p[0]
                    for p in after.permissions
                    if p[1] and not getattr(before.permissions, p[0])
                ]
                removed_perms = [
                    p[0]
                    for p in before.permissions
                    if p[1] and not getattr(after.permissions, p[0])
                ]

                if added_perms:
                    embed.add_field(
                        name="✅ صلاحيات أُعطيت:",
                        value=", ".join(added_perms).replace("_", " "),
                        inline=False,
                    )
                if removed_perms:
                    embed.add_field(
                        name="❌ صلاحيات سُحبت:",
                        value=", ".join(removed_perms).replace("_", " "),
                        inline=False,
                    )

            # 2. فحص تغير اسم الرتبة
            if before.name != after.name:
                embed.add_field(
                    name="📝 تغيير الاسم:",
                    value=f"من **{before.name}** إلى **{after.name}**",
                    inline=False,
                )

            # 3. فحص تغير لون الرتبة
            if before.color != after.color:
                embed.add_field(
                    name="🎨 تغيير اللون:",
                    value=f"من **{before.color}** إلى **{after.color}**",
                    inline=False,
                )

            embed.add_field(name="بواسطة المسؤول:", value=responsible_mod, inline=False)
            embed.set_footer(text=f"سجل التدقيق | {after.guild.name}")

            await log_channel.send(embed=embed)


# --- [نظام مراقبة القنوات الكتابية الشامل من الـ Audit Log] ---


@bot.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.TextChannel):
        return
    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697749774139453,
    }
    log_id = SERVER_LOGS.get(channel.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in channel.guild.audit_logs(
        action=discord.AuditLogAction.channel_create, limit=1
    ):
        embed = discord.Embed(
            title="🆕 إنشاء قناة كتابية جديدة",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="القناة:", value=channel.mention, inline=False)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=False)
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    if not isinstance(channel, discord.TextChannel):
        return
    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697749774139453,
    }
    log_id = SERVER_LOGS.get(channel.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in channel.guild.audit_logs(
        action=discord.AuditLogAction.channel_delete, limit=1
    ):
        embed = discord.Embed(
            title="🗑️ حذف قناة كتابية",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="اسم القناة المحذوفة:", value=channel.name, inline=False)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=False)
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_update(before, after):
    if not isinstance(after, discord.TextChannel):
        return
    SERVER_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697749774139453,
    }
    log_id = SERVER_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    # جلب تفاصيل التعديل من الـ Audit Log
    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.channel_update, limit=1
    ):
        if entry.target.id == after.id:
            embed = discord.Embed(
                title=f"⚙️ تعديل في القناة: {after.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(),
            )

            # فحص التغييرات الشائعة
            if before.name != after.name:
                embed.add_field(
                    name="📝 تغيير الاسم:",
                    value=f"من `{before.name}` إلى `{after.name}`",
                    inline=False,
                )

            if before.topic != after.topic:
                embed.add_field(
                    name="📖 تغيير الوصف:",
                    value=f"من `{before.topic or 'لا يوجد'}` إلى `{after.topic or 'لا يوجد'}`",
                    inline=False,
                )

            if before.overwrites != after.overwrites:
                embed.add_field(
                    name="🔐 تغيير الصلاحيات:",
                    value="تم تعديل الأذونات الخاصة بالقناة (قفل/فتح/صلاحيات أعضاء)",
                    inline=False,
                )

            embed.add_field(
                name="بواسطة المسؤول:", value=entry.user.mention, inline=False
            )
            await log_channel.send(embed=embed)
            break


# --- [نظام رادار الفويس الشامل - مرآة الـ Audit Log] ---


# 1. مراقبة إنشاء القنوات الصوتية
@bot.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.VoiceChannel):
        return
    SERVER_VOICE_LOGS = {
        1394284974680838388: 1479861318331793410,
        1182934425013604362: 1480697888257609778,
    }
    log_id = SERVER_VOICE_LOGS.get(channel.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in channel.guild.audit_logs(
        action=discord.AuditLogAction.channel_create, limit=1
    ):
        embed = discord.Embed(
            title="🔊 إنشاء قناة صوتية جديدة",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="اسم القناة:", value=f"#{channel.name}", inline=True)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=True)
        embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {channel.guild.name}")
        await log_channel.send(embed=embed)


# 2. مراقبة حذف القنوات الصوتية
@bot.event
async def on_guild_channel_delete(channel):
    if not isinstance(channel, discord.VoiceChannel):
        return
    SERVER_VOICE_LOGS = {
        1394284974680838388: 1479861318331793410,
        1182934425013604362: 1480697888257609778,
    }
    log_id = SERVER_VOICE_LOGS.get(channel.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in channel.guild.audit_logs(
        action=discord.AuditLogAction.channel_delete, limit=1
    ):
        embed = discord.Embed(
            title="🗑️ حذف قناة صوتية",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="اسم القناة:", value=channel.name, inline=True)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=True)
        embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {channel.guild.name}")
        await log_channel.send(embed=embed)


# 3. مراقبة تعديل الإعدادات والصلاحيات (Permissions)
@bot.event
async def on_guild_channel_update(before, after):
    if not isinstance(after, discord.VoiceChannel):
        return
    SERVER_VOICE_LOGS = {
        1394284974680838388: 1479861318331793410,
        1182934425013604362: 1480697888257609778,
    }
    log_id = SERVER_VOICE_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.channel_update, limit=1
    ):
        if entry.target.id == after.id:
            embed = discord.Embed(
                title=f"⚙️ تعديل إعدادات: {after.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(),
            )

            if before.name != after.name:
                embed.add_field(
                    name="📝 تغيير الاسم:",
                    value=f"من `{before.name}` إلى `{after.name}`",
                    inline=False,
                )

            if before.user_limit != after.user_limit:
                embed.add_field(
                    name="👥 سعة الروم:",
                    value=f"من `{before.user_limit or '∞'}` إلى `{after.user_limit or '∞'}`",
                    inline=False,
                )

            if before.bitrate != after.bitrate:
                embed.add_field(
                    name="🎙️ جودة الصوت:",
                    value=f"من `{before.bitrate // 1000}kbps` إلى `{after.bitrate // 1000}kbps`",
                    inline=False,
                )

            if before.overwrites != after.overwrites:
                embed.add_field(
                    name="🔐 الأذونات:",
                    value="تم تعديل صلاحيات (المنع/السماح) في الروم",
                    inline=False,
                )

            embed.add_field(
                name="بواسطة المسؤول:", value=entry.user.mention, inline=False
            )
            embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {after.guild.name}")
            await log_channel.send(embed=embed)
            break


# 4. مراقبة نقل الأعضاء وسحبهم (Voice State Update)
@bot.event
async def on_voice_state_update(member, before, after):
    SERVER_VOICE_LOGS = {
        1394284974680838388: 1479861318331793410,
        1182934425013604362: 1480697888257609778,
    }
    log_id = SERVER_VOICE_LOGS.get(member.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    # حالة سحب العضو أو نقله من قبل مسؤول
    if before.channel and after.channel and before.channel != after.channel:
        async for entry in member.guild.audit_logs(
            action=discord.AuditLogAction.member_move, limit=1
        ):
            if entry.target.id == member.id:
                embed = discord.Embed(
                    title="🚚 نقل عضو يدوياً",
                    color=discord.Color.dark_gold(),
                    timestamp=datetime.datetime.now(),
                )
                embed.add_field(name="العضو:", value=member.mention, inline=True)
                embed.add_field(name="من:", value=before.channel.name, inline=True)
                embed.add_field(name="إلى:", value=after.channel.name, inline=True)
                embed.add_field(
                    name="بواسطة المسؤول:", value=entry.user.mention, inline=False
                )
                embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {member.guild.name}")
                await log_channel.send(embed=embed)
                break


@bot.event
async def on_voice_state_update(member, before, after):
    # إعدادات رومات اللوق للسيرفرين
    SERVER_VOICE_LOGS = {
        1394284974680838388: 1479861318331793410,  # الأساسي
        1182934425013604362: 1480697888257609778,  # كوميهو
    }

    log_id = SERVER_VOICE_LOGS.get(member.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    if not log_channel:
        return

    embed = discord.Embed(timestamp=datetime.datetime.now())
    embed.set_author(name=member.name, icon_url=member.display_avatar.url)
    embed.set_footer(text=f"S🅾️UL S🅾️CIETY | {member.guild.name}")

    # 1. حالة دخول روم موجود مسبقاً
    if before.channel is None and after.channel is not None:
        embed.title = "📥 دخول قناة صوتية"
        embed.description = f"قام {member.mention} بالدخول إلى الفويس"
        embed.add_field(name="الروم:", value=f"🔊 {after.channel.name}", inline=True)
        embed.color = discord.Color.green()
        await log_channel.send(embed=embed)

    # 2. حالة الخروج من الفويس
    elif before.channel is not None and after.channel is None:
        embed.title = "📤 خروج من قناة صوتية"
        embed.description = f"قام {member.mention} بمغادرة الفويس"
        embed.add_field(
            name="الروم الذي غادره:", value=f"🔊 {before.channel.name}", inline=True
        )
        embed.color = discord.Color.red()
        await log_channel.send(embed=embed)

    # 3. حالة التنقل بين الرومات (نقل نفسه أو سحب يدوي)
    elif before.channel and after.channel and before.channel != after.channel:
        # البحث في الـ Audit Log للتأكد إذا كان "سحب" يدوي
        responsible_mod = None
        async for entry in member.guild.audit_logs(
            action=discord.AuditLogAction.member_move, limit=1
        ):
            # إذا كان التوقيت قريب جداً والهدف هو نفس العضو
            if entry.target.id == member.id:
                responsible_mod = entry.user.mention
                break

        if responsible_mod:
            embed.title = "🚚 نقل عضو (سحب يدوي)"
            embed.description = f"تم سحب {member.mention} بواسطة {responsible_mod}"
            embed.color = discord.Color.dark_gold()
        else:
            embed.title = "🔄 تغيير القناة الصوتية"
            embed.description = f"قام {member.mention} بتغيير الروم بنفسه"
            embed.color = discord.Color.blue()

        embed.add_field(name="من:", value=before.channel.name, inline=True)
        embed.add_field(name="إلى:", value=after.channel.name, inline=True)
        await log_channel.send(embed=embed)


# --- [نظام مراقبة الرتب - مرآة الـ Audit Log] ---


@bot.event
async def on_guild_role_create(role):
    # إعدادات روم لوق الرتب (تأكد من وضع الأيديات الصحيحة هنا)
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861118137794684,  # السيرفر الأساسي
        1182934425013604362: 1480697982671388845,  # كوميهو (أو غيره لروم الرتب)
    }

    log_id = SERVER_ROLE_LOGS.get(role.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in role.guild.audit_logs(
        action=discord.AuditLogAction.role_create, limit=1
    ):
        embed = discord.Embed(
            title="✨ إنشاء رتبة جديدة",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="الرتبة:", value=role.name, inline=True)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=True)
        embed.set_footer(text=f"ID: {role.id} | {role.guild.name}")
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_delete(role):
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697982671388845,
    }
    log_id = SERVER_ROLE_LOGS.get(role.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in role.guild.audit_logs(
        action=discord.AuditLogAction.role_delete, limit=1
    ):
        embed = discord.Embed(
            title="🗑️ حذف رتبة",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="اسم الرتبة المحذوفة:", value=role.name, inline=True)
        embed.add_field(name="بواسطة المسؤول:", value=entry.user.mention, inline=True)
        embed.set_footer(text=f"سجل الرتب | {role.guild.name}")
        await log_channel.send(embed=embed)


@bot.event
async def on_guild_role_update(before, after):
    SERVER_ROLE_LOGS = {
        1394284974680838388: 1479861118137794684,
        1182934425013604362: 1480697982671388845,
    }
    log_id = SERVER_ROLE_LOGS.get(after.guild.id)
    if not log_id:
        return
    log_channel = bot.get_channel(log_id) or await bot.fetch_channel(log_id)

    async for entry in after.guild.audit_logs(
        action=discord.AuditLogAction.role_update, limit=1
    ):
        if entry.target.id == after.id:
            embed = discord.Embed(
                title=f"⚙️ تعديل في رتبة: {after.name}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(),
            )

            # فحص التغييرات (الاسم، اللون، الصلاحيات)
            if before.name != after.name:
                embed.add_field(
                    name="📝 تغيير الاسم:",
                    value=f"من `{before.name}` إلى `{after.name}`",
                    inline=False,
                )

            if before.color != after.color:
                embed.add_field(
                    name="🎨 تغيير اللون:",
                    value=f"من `{before.color}` إلى `{after.color}`",
                    inline=False,
                )

            if before.permissions != after.permissions:
                embed.add_field(
                    name="🔐 تغيير الصلاحيات:",
                    value="تم تعديل أذونات الرتبة",
                    inline=False,
                )

            embed.add_field(
                name="بواسطة المسؤول:", value=entry.user.mention, inline=False
            )
            await log_channel.send(embed=embed)
            break


# --- [نظام الردود التلقائية - نسخة الـ Embed] ---


@bot.listen("on_message")
async def auto_reply_system(message):
    # تجاهل رسائل البوتات والرسائل الخاصة
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()

    # 1. الرد على كوميهو أو kumiho
    if content == "كوميهو" or content == "kumiho":
        embed = discord.Embed(description="**هلا آمر، لبيه؟** 🦊", color=0x2F3136)
        await message.reply(embed=embed)

    # 2. الرد على السلام عليكم
    elif "السلام عليكم" in content:
        embed = discord.Embed(
            description="**وعليكم السلام ورحمة الله وبركاته، نورت السيرفر يا غالي** ✨",
            color=discord.Color.green(),
        )
        await message.reply(embed=embed)

    # 3. الرد على صباح الخير
    elif "صباح الخير" in content:
        embed = discord.Embed(
            description="**صباح النور والسرور، يومك سعيد ومليء بالإنجازات** ☀️",
            color=0xFFD700,
        )
        await message.reply(embed=embed)

    # 4. الرد على مساء الخير
    elif "مساء الخير" in content:
        embed = discord.Embed(
            description="**مساء الورد والأنوار، نورتنا بطلتك المسائية** ✨",
            color=0x5865F2,
        )
        await message.reply(embed=embed)


bot.run(os.environ["TOKEN"])
