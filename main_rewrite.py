import json
import discord
import sqlite3
from uuid import uuid4

guild_ids = [732561587788972112, 1220365157113532426]
with open("keys.json", "r") as f:
    keys = json.load(f)
token = keys["discord-token"]
bot = discord.Bot()



class Embed_Tool:
    def build_request_embed(request_id: str):
        build_request = database.get_build_request(request_id)
        request_id, category_name, sender_id, status, processor_user_id = build_request

        embed = {
            "title": "Build Request",
            "fields": [
                {"name": "リクエストID", "value": request_id, "inline": False},
                {"name": "カテゴリー名", "value": category_name, "inline": False},
                {"name": "送信者", "value": sender_id, "inline": False},
                {"name": "送信者ID", "value": sender_id, "inline": False},
                {"name": "状態", "value": status, "inline": False},
                {"name": "担当者", "value": processor_user_id, "inline": False},
                {"name": "担当者ID", "value": processor_user_id, "inline": False},
            ]
        }
        if status == "待機中":
            embed["color"] = discord.Color.blurple()
        elif status == "承認":
            embed["color"] = discord.Color.green()
        elif status == "拒否":
            embed["color"] = discord.Color.red()
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
        cur.execute("CREATE TABLE IF NOT EXISTS build_request(request_id TEXT PRIMARY KEY, category_name TEXT, sender_id INTEGER, status TEXT, processor_user_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS category(build_id TEXT PRIMARY KEY, category_id INTEGER, guild_id INTEGER, name TEXT, moderator_channel_id INTEGER, owner_id INTEGER, role_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS guild_settings(guild_id INTEGER PRIMARY KEY, moderator_channel_id INTEGER, notification_channel_id INTEGER, moderator_role_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS join_request(request_id INTEGER PRIMARY KEY, build_id TEXT, sender_id INTEGER, status TEXT, processor_user_id INTEGER)")
    
    def add_build_request(self, request_id: str, category_name: str, sender_id: int, status: str, processor_user_id: int):
        cur = self.db.cursor()
        sql = f"INSERT INTO build_request VALUES ('{request_id}', '{category_name}', {sender_id}, '{status}', {processor_user_id})"
        cur.execute(sql)
        self.db.commit()
    
    def update_status_build_request(self, request_id: str, processor_user_id: int, status: str):
        cur = self.db.cursor()
        sql = f"UPDATE build_request SET status = '{status}', processor_user_id = {processor_user_id} WHERE request_id = '{request_id}'"
        cur.execute(sql)
        self.db.commit()
    
    def add_category(self, build_id: str, category_id: int, guild_id: int, name: str, moderator_channel_id: int, owner_id: int, role_id: int):
        cur = self.db.cursor()
        sql = f"INSERT INTO category VALUES ('{build_id}', {category_id}, {guild_id}, '{name}', {moderator_channel_id}, {owner_id}, {role_id})"
        cur.execute(sql)
        self.db.commit()
    
    def add_join_request(self, request_id: str, build_id: str, sender_id: int, status: str, processor_user_id: int):
        cur = self.db.cursor()
        sql = f"INSERT INTO join_request VALUES ('{request_id}', '{build_id}', {sender_id}, '{status}', {processor_user_id})"
        cur.execute(sql)
        self.db.commit()

    def update_status_join_request(self, request_id: str, processor_user_id: int, status: str):
        cur = self.db.cursor()
        sql = f"UPDATE join_request SET status = '{status}', processor_user_id = {processor_user_id} WHERE request_id = '{request_id}'"
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

    def get_guild_settings(self, guild_id: int):
        cur = self.db.cursor()
        sql = f"SELECT * FROM guild_settings WHERE guild_id = {guild_id}"
        cur.execute(sql)
        return cur.fetchone()
    def close(self):
        self.db.close()
    
class BuildRequestView(discord.ui.View):
    @discord.ui.button(label="Accept",row=0, style=discord.ButtonStyle.green)
    async def accept_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        message = interaction.message
        embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
        request_id = embed_data["リクエストID"]
        database.update_status_build_request(request_id, interaction.user.id, "承認")
        request_id, category_name, sender_id, status, processor_user_id = database.get_build_request(request_id)
        sender = bot.get_user(sender_id)
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

        guild_data = interaction.guild
        database.add_category(request_id, category.id, guild_data.id, category_name, moderator_channel.id, sender_id, new_role.id)
        
    
    @discord.ui.button(label="Deny", row=1, style=discord.ButtonStyle.red)
    async def deny_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        message = interaction.message
        embed_data = Embed_Tool.embed_to_dict(message.embeds[0])
        request_id = embed_data["リクエストID"]
        database.update_status_build_request(request_id, interaction.user.id, "拒否")
        embed = Embed_Tool.build_request_embed(request_id)
        await build_request.sender.send("Build Request Denied", embed=embed)
        await interaction.message.edit("", embed=embed, view=None)

class JoinRequestView(discord.ui.View):
    @discord.ui.button(label="Accept",row=0, style=discord.ButtonStyle.green)
    async def accept_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        pass

    @discord.ui.button(label="Deny", row=1, style=discord.ButtonStyle.red)
    async def deny_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        pass
    
    
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(guild_ids=guild_ids)
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hello!")

# @bot.slash_command(guild_ids=guild_ids)
# async def join_request(ctx: discord.ApplicationContext, role: discord.Role):
#     await ctx.respond(f"Join Request for {role.name} sent", ephemeral=True)
#     category_data = data.get_category_with_role_id(ctx.guild_id, role.id)
#     if not category_data:
#         await ctx.respond("Category not found", ephemeral=True)
#         return
#     category_id = category_data["category"]
#     owner_id = category_data["owner"]
#     moderator_channel_id = category_data.get("moderator_channel", None)
#     if not category_id or not moderator_channel_id or not owner_id:
#         await ctx.respond("エラーが発生しました", ephemeral=True)
#         return
#     owner = bot.get_user(owner_id)
#     moderator_channel = bot.get_channel(moderator_channel_id)
#     await moderator_channel.send(f"{owner.mention}{ctx.author.display_name} さんが参加申請を送りました。", view=JoinRequestView())

@bot.slash_command(guild_ids=guild_ids)
async def set_moderator_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    database.update_guild_settings("moderator_channel", ctx.guild_id, channel.id)
    await ctx.respond(f"Channel set to {channel.id}", ephemeral=True)


@bot.slash_command(guild_ids=guild_ids)
async def set_notification_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    database.update_guild_settings("notification_channel", ctx.guild_id, channel.id)
    await ctx.respond(f"Channel set to {channel.id}", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def test_send(ctx: discord.ApplicationContext, message: str):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    _, moderation_channel_id, _, _= guild_settings
    if not moderation_channel_id:
        await ctx.respond("No channel set")
        return
    channel = bot.get_channel(moderation_channel_id)
    await channel.send(message)
    await ctx.respond("Message sent", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def set_guild_settings(ctx: discord.ApplicationContext, moderation_channel: discord.TextChannel, notification_channel: discord.TextChannel, moderation_role: discord.Role):
    database.add_guild_settings(ctx.guild_id, moderation_channel.id, notification_channel.id, moderation_role.id)
    await ctx.respond("Guild settings set", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def build_request(ctx: discord.ApplicationContext, name: str):
    guild_settings = database.get_guild_settings(ctx.guild_id)
    print(guild_settings)
    _, moderation_channel_id, _, _ = guild_settings
    if not moderation_channel_id:
        await ctx.respond("No channel set")
        return
    moderation_channel = bot.get_channel(moderation_channel_id)
    view = BuildRequestView()
    message = await moderation_channel.send("loading")
    request_id = str(uuid4())
    database.add_build_request(request_id, name, ctx.author.id, "待機中", 0)
    embed = Embed_Tool.build_request_embed(request_id)
    await message.edit("", embed=embed, view=view)
    await ctx.respond(f"", embed=embed())

@bot.slash_command(guild_ids=guild_ids)
async def stop(ctx: discord.ApplicationContext):
    if ctx.author.id == 423662596533518358:
        await ctx.respond("Bot stopped", ephemeral=True)
        database.close()
        await bot.close()
    else:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)

database = DataBase()
bot.run(token)