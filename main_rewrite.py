import json
import discord
import sqlite3
from uuid import uuid4
# 一時的な変更
# guild_ids = [732561587788972112, 1220365157113532426]
guild_ids = [1326334355832049704]
with open("keys.json", "r") as f:
    keys = json.load(f)
token = keys["discord-token"]
bot = discord.Bot()



class Embed_Tool:
    def build_request_embed(request_id: str):
        build_request = database.get_build_request(request_id)
        request_id, category_name, sender_id, sender_name, status, processor_user_id, processor_user_name = build_request
        embed = discord.Embed(title="Build Request")
        embed.add_field(name="リクエストID", value=request_id, inline=False)
        embed.add_field(name="カテゴリー名", value=category_name, inline=False)
        embed.add_field(name="送信者", value=sender_name, inline=False)
        embed.add_field(name="送信者ID", value=sender_id, inline=False)
        embed.add_field(name="状態", value=status, inline=False)
        embed.add_field(name="担当者", value=processor_user_name, inline=False)
        embed.add_field(name="担当者ID", value=processor_user_id, inline=False)
        if status == "待機中":
            embed.color = discord.Color.blurple()
        elif status == "承認":
            embed.color = discord.Color.green()
        elif status == "拒否":
            embed.color = discord.Color.red()
        return embed

    def join_request_embed(request_id: str):
        join_request = database.get_join_request(request_id)
        request_id, build_id, category_name, sender_id, sender_name, status, processor_user_id, processor_user_name = join_request
        embed = discord.Embed(title="Join Request")
        embed.add_field(name="リクエストID", value=request_id, inline=False)
        embed.add_field(name="ビルドID", value=build_id, inline=False)
        embed.add_field(name="カテゴリー名", value=category_name, inline=False)
        embed.add_field(name="送信者", value=sender_name, inline=False)
        embed.add_field(name="送信者ID", value=sender_id, inline=False)
        embed.add_field(name="状態", value=status, inline=False)
        embed.add_field(name="担当者", value=processor_user_name, inline=False)
        embed.add_field(name="担当者ID", value=processor_user_id, inline=False)
        if status == "待機中":
            embed.color = discord.Color.blurple()
        elif status == "承認":
            embed.color = discord.Color.green()
        elif status == "拒否":
            embed.color = discord.Color.red()
        return embed
    
    def embed_to_dict(embed: discord.Embed):
        embed_dict = embed.to_dict()
        result = {}
        for field in embed_dict["fields"]:
            name, value = field["name"], field["value"]
            try:
                value = int(value)
            except:
                pass
            result.update({name: value})
        return result
        
class DataBase:
    def __init__(self):
        db_path = "db.sqlite3"
        self.db = sqlite3.connect(db_path)
        cur = self.db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS build_request(request_id TEXT PRIMARY KEY, category_name TEXT, sender_id INTEGER, sender_name TEXT, status TEXT, processor_user_id INTEGER, processor_name TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS category(build_id TEXT PRIMARY KEY, category_id INTEGER, guild_id INTEGER, name TEXT, moderator_channel_id INTEGER, owner_id INTEGER, role_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS guild_settings(guild_id INTEGER PRIMARY KEY, moderator_channel_id INTEGER, notification_channel_id INTEGER, moderator_role_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS join_request(request_id TEXT PRIMARY KEY, build_id TEXT, category_name TEXT, sender_id INTEGER, sender_name TEXT, status TEXT, processor_user_id INTEGER, processor_name TEXT)")
    
    def add_build_request(self, request_id: str, category_name: str, sender_id: int, sender_name: str, status: str, processor_user_id: int, processor_name: str):
        cur = self.db.cursor()
        sql = f"INSERT INTO build_request VALUES ('{request_id}', '{category_name}', {sender_id}, '{sender_name}', '{status}', {processor_user_id}, '{processor_name}')"
        cur.execute(sql)
        self.db.commit()
    
    def update_status_build_request(self, request_id: str, processor_user_id: int, processor_name: str, status: str):
        cur = self.db.cursor()
        sql = f"UPDATE build_request SET status = '{status}', processor_user_id = {processor_user_id}, processor_name = '{processor_name}' WHERE request_id = '{request_id}'"
        cur.execute(sql)
        self.db.commit()
    
    def add_category(self, build_id: str, category_id: int, guild_id: int, name: str, moderator_channel_id: int, owner_id: int, role_id: int):
        cur = self.db.cursor()
        sql = f"INSERT INTO category VALUES ('{build_id}', {category_id}, {guild_id}, '{name}', {moderator_channel_id}, {owner_id}, {role_id})"
        cur.execute(sql)
        self.db.commit()
    
    def add_join_request(self, request_id: str, build_id: str, category_name: str, sender_id: int, sender_name: str, status: str, processor_user_id: int, processor_user_name: str):
        cur = self.db.cursor()
        sql = f"INSERT INTO join_request VALUES ('{request_id}', '{build_id}', '{category_name}',{sender_id}, '{sender_name}', '{status}', {processor_user_id}, '{processor_user_name}')"
        cur.execute(sql)
        self.db.commit()

    def update_status_join_request(self, request_id: str, processor_user_id: int, processor_user_name: str, status: str):
        cur = self.db.cursor()
        sql = f"UPDATE join_request SET status = '{status}', processor_user_id = {processor_user_id}, processor_name = '{processor_user_name}' WHERE request_id = '{request_id}'"
        cur.execute(sql)
        self.db.commit()
    
    def add_guild_settings(self, guild_id: int, moderator_channel_id: int, notification_channel_id: int, moderator_role_id: int):
        cur = self.db.cursor()
        sql = f"INSERT INTO guild_settings VALUES ({guild_id}, {moderator_channel_id}, {notification_channel_id}, {moderator_role_id})"
        cur.execute(sql)
        self.db.commit()
    
    def update_guild_settings(self, setting_name: str, guild_id: int, value: int):
        cur = self.db.cursor()
        sql = f"REPLACE INTO guild_settings SET {setting_name} = {value} WHERE guild_id = {guild_id}"
        cur.execute(sql)
        self.db.commit()
    
    def get_build_request(self, request_id: str):
        cur = self.db.cursor()
        sql = f"SELECT * FROM build_request WHERE request_id = '{request_id}'"
        cur.execute(sql)
        return cur.fetchone()
    
    def get_join_request(self, request_id: str):
        cur = self.db.cursor()
        sql = f"SELECT * FROM join_request WHERE request_id = '{request_id}'"
        cur.execute(sql)
        return cur.fetchone()
    
    def get_category(self, build_id: str):
        cur = self.db.cursor()
        sql = f"SELECT * FROM category WHERE build_id = '{build_id}'"
        cur.execute(sql)
        return cur.fetchone()
    
    def get_category_with_role_id(self, guild_id: int, role_id: int):
        cur = self.db.cursor()
        sql = f"SELECT * FROM category WHERE guild_id = {guild_id} AND role_id = {role_id}"
        cur.execute(sql)
        return cur.fetchone()

    def get_guild_settings(self, guild_id: int):
        cur = self.db.cursor()
        sql = f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}"
        cur.execute(sql)
        return cur.fetchone()
    
    def get_build_request_list(self):
        cur = self.db.cursor()
        sql = f"SELECT request_id, category_name, sender_name FROM build_request WHERE status = '待機中'"
        cur.execute(sql)
        return cur.fetchall()

    def get_join_request_list(self):
        cur = self.db.cursor()
        sql = f"SELECT request_id, build_id, category_name, sender_name FROM join_request WHERE status = '待機中'"
        cur.execute(sql)
        return cur.fetchall()
    
    def close(self):
        self.db.close()

class BuildRequestAcceptButton(discord.ui.Button):
    def __init__(self, request_id: str):
        super().__init__(discord.ui.Button(
            label="Accept",
            custom_id=f"build_accept_{request_id}",
            style=discord.ButtonStyle.green
        ))

class BuildRequestDenyButton(discord.ui.Button):
    def __init__(self, request_id: str):
        super().__init__(discord.ui.Button(
            label="Deny",
            custom_id=f"build_deny_{request_id}",
            style=discord.ButtonStyle.red
        ))

class JoinRequestAcceptButton(discord.ui.Button):
    def __init__(self, request_id: str):
        super().__init__(discord.ui.Button(
            label="Accept",
            custom_id=f"join_accept_{request_id}",
            style=discord.ButtonStyle.green
        ))

class JoinRequestDenyButton(discord.ui.Button):
    def __init__(self, request_id: str):
        super().__init__(discord.ui.Button(
            label="Deny",
            custom_id=f"join_deny_{request_id}",
            style=discord.ButtonStyle.red
        ))

class BuildRequestView(discord.ui.View):
    def __init__(self, request_id: str):
        super().__init__(timeout=None)
        self.add_item(BuildRequestAcceptButton(request_id))
        self.add_item(BuildRequestDenyButton(request_id))
    

class JoinRequestView(discord.ui.View):
    def __init__(self, request_id: str):
        super().__init__(timeout=None)
        self.add_item(JoinRequestAcceptButton(request_id))
        self.add_item(JoinRequestDenyButton(request_id))
    
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(guild_ids=guild_ids)
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hello!")
    
@bot.slash_command(guild_ids=guild_ids)
async def join_request(ctx: discord.ApplicationContext, role: discord.Role):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if guild_settings is None:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    category = database.get_category_with_role_id(ctx.guild_id, role.id)
    if category is None:
        await ctx.respond("Category not found", ephemeral=True)
        return
    if ctx.author.get_role(role.id):
        await ctx.respond("You already have this role", ephemeral=True)
        return
    #build_id TEXT PRIMARY KEY, category_id INTEGER, guild_id INTEGER, name TEXT, moderator_channel_id INTEGER, owner_id INTEGER, role_id INTEGE
    build_id, category_id, guild_id, name, moderator_channel_id, owner_id, role_id = category
    request_id = str(uuid4())
    database.add_join_request(request_id, build_id, name, ctx.author.id, ctx.author.display_name, "待機中", 0, "---")
    guild = ctx.guild
    embed = Embed_Tool.join_request_embed(request_id)
    await guild.get_channel(moderator_channel_id).send(f"{ctx.guild.get_member(owner_id).mention}", embed=embed, view=JoinRequestView(request_id))
    await ctx.respond(f"Join request sent to {role.name}", ephemeral=True)
    
    

@bot.slash_command(guild_ids=guild_ids)
async def set_moderator_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if guild_settings is None:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    _, _, _, moderator_role = guild_settings
    if not ctx.author.get_role(moderator_role):
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    database.update_guild_settings("moderator_channel", ctx.guild_id, channel.id)
    await ctx.respond(f"Channel set to {channel.id}", ephemeral=True)


@bot.slash_command(guild_ids=guild_ids)
async def set_notification_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if guild_settings is None:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    _, _, _, moderator_role = guild_settings
    if not ctx.author.get_role(moderator_role):
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    database.update_guild_settings("notification_channel", ctx.guild_id, channel.id)
    await ctx.respond(f"Channel set to {channel.id}", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def set_moderator_role(ctx: discord.ApplicationContext, role: discord.Role):
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    database.update_guild_settings("moderator_role", ctx.guild_id, role.id)
    await ctx.respond(f"Role set to {role.id}", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def set_guild_settings(ctx: discord.ApplicationContext, moderation_channel: discord.TextChannel, notification_channel: discord.TextChannel, moderation_role: discord.Role):
    guild_setting = database.get_guild_settings(ctx.guild_id)
    if guild_setting is not None:
        await ctx.respond("Guild settings already set", ephemeral=True)
        return
    database.add_guild_settings(ctx.guild_id, moderation_channel.id, notification_channel.id, moderation_role.id)
    await ctx.respond("Guild settings set", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def build_request(ctx: discord.ApplicationContext, name: str):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if not guild_settings:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    _, moderation_channel_id, _, _ = guild_settings
    if not moderation_channel_id:
        await ctx.respond("No channel set", ephemeral=True)
        return
    moderation_channel = ctx.guild.get_channel(moderation_channel_id)
    view = BuildRequestView(request_id)
    message = await moderation_channel.send("loading")
    request_id = str(uuid4())
    database.add_build_request(request_id, name, ctx.author.id, ctx.author.display_name,"待機中", 0, "---")
    embed = Embed_Tool.build_request_embed(request_id)
    await message.edit("", embed=embed, view=view)
    await ctx.respond(f"", embed=embed)

@bot.slash_command(guild_ids=guild_ids)
async def stop(ctx: discord.ApplicationContext):
    if ctx.author.id == 423662596533518358:
        await ctx.respond("Bot stopped", ephemeral=True)
        database.close()
        await bot.close()
    else:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def get_build_request_list(ctx: discord.ApplicationContext):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if not guild_settings:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    _, _, _, moderation_role_id = guild_settings
    if not moderation_role_id:
        await ctx.respond("No role set")
        return
    if not ctx.author.get_role(moderation_role_id):
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    result = ""
    for request_id, category_name, sender_name in database.get_build_request_list():
        result += f"ID: {request_id} \nカテゴリー名: {category_name} \n送信者: {sender_name}\n\n"
    if not result:
        result = "Build request not found"
    await ctx.respond(result, ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def get_join_request_list(ctx: discord.ApplicationContext):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    if not guild_settings:
        await ctx.respond("Guild settings not found", ephemeral=True)
        return
    _, _, _, moderation_role_id = guild_settings
    if not moderation_role_id:
        await ctx.respond("No role set")
        return
    if not ctx.author.get_role(moderation_role_id):
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    result = ""
    for request_id, build_id, category_name, sender_name in database.get_join_request_list():
        result += f"ID: {request_id} \nBuild ID: {build_id} \nカテゴリー名: {category_name} \n送信者: {sender_name}\n\n"
    if not result:
        result = "Join request not found"
    await ctx.respond(result, ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def help(ctx: discord.ApplicationContext):
    result = """```
    /build_request [任意の名前]- Build requestを作成するときに使う
    -承認されると指定した名前で新しくカテゴリーが作成され、そのカテゴリーの管理権限が渡されます。
    -同じ名前でロールが作成され、そのロールがついているメンバーにしかそのカテゴリーは表示されません
    
    /join_request [任意のロール]- 入りたいところのロールを選んでJoin requestを送るときに使う
    -入りたいカテゴリーと同じ名前のロールを選択してください。
    -承認されるとそのロールが付与されます。
    
    /set_guild_settings [管理用チャンネル] [通知用チャンネル] [管理者ロール]- サーバーでのbotの初期設定用のコマンド(管理者のみ)
    /set_moderation_channel [管理用チャンネル]- Build requestが届くチャンネルを設定(管理者のみ)
    /set_notification_channel [通知用チャンネル]- なにかしらに使う予定のチャンネルを設定(管理者のみ)
    /set_moderator_role [管理者ロール]- このbotの管理者として扱うロールを設定する(サーバーでのロール管理の権限が必要)
    /get_build_request_list - 待機中のBuild request一覧(管理者のみ)
    /get_join_request_list - 待機中のJoin request一覧(管理者のみ)
    /stop - Botを止める(ユーのみ)```
    """
    await ctx.respond(result, ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def accept_build_request(ctx: discord.ApplicationContext, request_id: str):
    database.update_status_build_request(request_id, ctx.author.id, ctx.author.display_name, "承認")
    build_request = database.get_build_request(request_id)
    if not build_request:
        await ctx.respond("Build request not found", ephemeral=True)
        return
    request_id, category_name, sender_id, sender_name, status, processor_user_id, processor_name = build_request
    guild = ctx.guild
    guild_settings = database.get_guild_settings(guild.id)
    if not guild_settings:
        await ctx.respond("guild settings not found", ephemeral=True)
        return
    _, _, _, moderator_role_id = guild_settings
    if not ctx.author.get_role(moderator_role_id):
        await ctx.respond("You are not authorized to use this command", ephemeral=True)
        return
    new_role = await guild.create_role(name=category_name)
    sender = guild.get_member(sender_id)
    general_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        new_role: discord.PermissionOverwrite(view_channel=True),
        sender: discord.PermissionOverwrite(manage_channels=True)
    }
    moderator_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        new_role: discord.PermissionOverwrite(view_channel=False),
        sender: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
    }

    category = await guild.create_category(name=category_name, overwrites=general_overwrites)
    general_channel = await guild.create_text_channel(name="一般", category=category)
    moderator_channel = await guild.create_text_channel(name="管理者用", category=category, overwrites=moderator_overwrites)
    await general_channel.send(f"作成が完了しました")
    await moderator_channel.send(f"{sender.mention} 参加申請があった場合はこのチャンネルに通知されます。このチャンネルはこのカテゴリーの管理者にのみ表示されます。")
    await sender.add_roles(new_role)
    database.add_category(request_id, category.id, guild.id, category_name, moderator_channel.id, sender_id, new_role.id)

    embed = Embed_Tool.build_request_embed(request_id)
    await ctx.respond("Build Request Accepted", embed=embed)


@bot.slash_command(guild_ids=guild_ids)
async def accept_join_request(ctx: discord.ApplicationContext, request_id: str):
    database.update_status_join_request(request_id, ctx.author.id, ctx.author.display_name, "承認")
    join_request = database.get_join_request(request_id)
    if not join_request:
        await ctx.respond("Join request not found", ephemeral=True)
        return
    request_id, build_id, category_name, sender_id, sernder_name, status, processor_user_id, processor_user_name = join_request
    category = database.get_category(build_id)
    build_id, category_id, guild_id, name, moderator_channel_id, owner_id, role_id = category
    if ctx.channel_id != moderator_channel_id:
        await ctx.respond("Here is not moderation channel", ephemeral=True)
        return
    role = ctx.guild.get_role(role_id)
    sender = ctx.guild.get_member(sender_id)
    embed = Embed_Tool.join_request_embed(request_id)
    await sender.add_roles(role)
    await sender.send("Join Request Accepted", embed=embed)
    await ctx.respond("Join Request Accepted", embed=embed)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        pass
    custom_id = interaction.data.get("custom_id")
    if custom_id:
        if custom_id.startswith("build_accept_"):
            await build_request_accept_button_callback(interaction)
        elif custom_id.startswith("build_deny_"):
            await build_request_deny_button_callback(interaction)
        elif custom_id.startswith("join_accept_"):
            await join_request_accept_button_callback(interaction)
        elif custom_id.startswith("join_deny_"):
            await join_request_deny_button_callback(interaction)

async def build_request_accept_button_callback(interaction: discord.Interaction):
    message = interaction.message
    embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
    request_id = embed_data["リクエストID"]
    database.update_status_build_request(request_id, interaction.user.id, interaction.user.display_name, "承認")
    request_id, category_name, sender_id, sernder_name, status, processor_user_id, processor_user_name = database.get_build_request(request_id)
    sender = interaction.guild.get_member(sender_id)
    embed = Embed_Tool.build_request_embed(request_id)
    await sender.send("Build Request Accepted", embed=embed)
    await interaction.message.edit("", embed=embed, view=None)

    guild = interaction.guild
    new_role = await guild.create_role(name=category_name)

    general_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        new_role: discord.PermissionOverwrite(view_channel=True),
        sender: discord.PermissionOverwrite(manage_channels=True)
    }
    moderator_overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        new_role: discord.PermissionOverwrite(view_channel=False),
        sender: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
    }

    category = await guild.create_category(name=category_name, overwrites=general_overwrites)
    general_channel = await guild.create_text_channel(name="一般", category=category)
    moderator_channel = await guild.create_text_channel(name="管理者用", category=category, overwrites=moderator_overwrites)
    await general_channel.send(f"作成が完了しました")
    await moderator_channel.send(f"{sender.mention} 参加申請があった場合はこのチャンネルに通知されます。このチャンネルはこのカテゴリーの管理者にのみ表示されます。")
    await sender.add_roles(new_role)

    guild_data = interaction.guild
    database.add_category(request_id, category.id, guild_data.id, category_name, moderator_channel.id, sender_id, new_role.id)

async def build_request_deny_button_callback(interaction: discord.Interaction):
    message = interaction.message
    embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
    request_id = embed_data["リクエストID"]
    database.update_status_build_request(request_id, interaction.user.id, interaction.user.display_name, "拒否")
    request_id, category_name, sender_id, sernder_name, status, processor_user_id, processor_user_name = database.get_build_request(request_id)
    embed = Embed_Tool.build_request_embed(request_id)
    sender = interaction.guild.get_member(sender_id)
    await sender.send("Build Request Denied", embed=embed)
    await interaction.message.edit("", embed=embed, view=None)

async def join_request_accept_button_callback(interaction: discord.Interaction):
    message = interaction.message
    embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
    request_id = embed_data["リクエストID"]
    database.update_status_join_request(request_id, interaction.user.id, interaction.user.display_name, "承認")
    request_id, build_id, category_name, sender_id, sernder_name, status, processor_user_id, processor_user_name = database.get_join_request(request_id)
    category = database.get_category(build_id)
    build_id, category_id, guild_id, name, moderator_channel_id, owner_id, role_id = category
    role = interaction.guild.get_role(role_id)
    sender = interaction.guild.get_member(sender_id)
    embed = Embed_Tool.join_request_embed(request_id)
    await sender.add_roles(role)
    await sender.send("Join Request Accepted", embed=embed)
    await interaction.message.edit("", embed=embed, view=None)

async def join_request_deny_button_callback(interaction: discord.Interaction):
    message = interaction.message
    embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
    request_id = embed_data["リクエストID"]
    database.update_status_join_request(request_id, interaction.user.id, interaction.user.display_name, "拒否")
    request_id, category_name, sender_id, sernder_name, status, processor_user_id, processor_user_name = database.get_join_request(request_id)
    embed = Embed_Tool.join_request_embed(request_id)
    sender = interaction.guild.get_member(sender_id)
    await sender.send("Join Request Denied", embed=embed)
    await interaction.message.edit("", embed=embed, view=None)



database = DataBase()
bot.run(token)