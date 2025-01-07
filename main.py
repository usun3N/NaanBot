import json
import discord
import sqlite3

guild_ids = [732561587788972112, 1220365157113532426]
with open("keys.json", "r") as f:
    keys = json.load(f)
token = keys["discord-token"]
build_request_dict = {}
bot = discord.Bot()

class Data_Storage:
    def __init__(self):
        try:
            with open("data.json") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
            with open("data.json", "w") as f:
                json.dump(data, f)
        self.data = data
    
    def set_channel(self, guild_id, channel_id):
        guild_data = self.data.get(str(guild_id), {})
        guild_data["send_channel_id"] = str(channel_id)
        self.data[str(guild_id)] = guild_data
    
    def get_channel(self, guild_id):
        return self.data.get(str(guild_id), {}).get("send_channel_id", None)
    
    def save(self):
        with open("data.json", "w") as f:
            json.dump(self.data, f)
    
    def add_category(self, guild_id, category_id, moderator_channel_id, owner_id, role_id):
        data = {
            "category": str(category_id),
            "moderator": str(moderator_channel_id),
            "owner": str(owner_id),
            "role": str(role_id)
        }
        guild_data = self.data.get(str(guild_id), {})
        category_data = guild_data.get("categories", {})
        category_data.update({role_id: data})
        guild_data["categories"] = category_data
        self.data[str(guild_id)] = guild_data
    
    def get_category_with_role_id(self, guild_id, role_id):
        guild_data = self.data.get(str(guild_id), {})
        category_data = guild_data.get("categories", {})
        return category_data.get(role_id, None)

class BuildRequest:
    def __init__(self, request_id: int, category_name: str, sender: discord.User, status="待機中"):
        self.request_id = request_id
        self.name = category_name
        self.sender = sender
        self.status = status

    def accept(self, user: discord.User):
        self.status = "承認"
        self.user = user

    def deny(self, user: discord.User):
        self.status = "拒否"
        self.user = user

    def get_embed(self):
        embed = discord.Embed(
            title="Build Request"
        )
        embed.add_field(name="リクエストID", value=self.request_id, inline=False)
        embed.add_field(name="カテゴリー名", value=self.name, inline=False)
        embed.add_field(name="送信者", value=self.sender.display_name, inline=False)
        embed.add_field(name="状態", value=self.status, inline=False)
        if self.status == "待機中":
            embed.color = discord.Color.blurple()
        else:
            embed.add_field(name="担当者", value=self.user.display_name, inline=False)
            if self.status == "承認":
                embed.color = discord.Color.green()
            elif self.status == "拒否":
                embed.color = discord.Color.red()
        return embed
    
    def get_send_embed(self):
        embed = discord.Embed(
            title="Build Request"
        )
        embed.add_field(name="リクエストID", value=self.request_id, inline=False)
        embed.add_field(name="カテゴリー名", value=self.name, inline=False)
        embed.add_field(name="送信者", value=self.sender.display_name, inline=False)
        return embed


    
class BuildRequestView(discord.ui.View):
    @discord.ui.button(label="Accept",row=0, style=discord.ButtonStyle.green)
    async def accept_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        message_id = interaction.message.id
        build_request = build_request_dict[message_id]
        build_request.accept(interaction.user)
        embed = build_request.get_embed()
        await build_request.sender.send("Build Request Accepted", embed=embed)
        build_request_dict.pop(message_id)
        await interaction.message.edit("", embed=embed, view=None)

        guild = interaction.guild
        new_role = await guild.create_role(name=build_request.name)

        general_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            new_role: discord.PermissionOverwrite(view_channel=True),
            build_request.sender: discord.PermissionOverwrite(manage_channels=True)
        }
        moderator_overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            new_role: discord.PermissionOverwrite(view_channel=False),
            build_request.sender: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
        }

        category = await guild.create_category(name=build_request.name, overwrites=general_overwrites)
        general_channel = await guild.create_text_channel(name="一般", category=category)
        moderator_channel = await guild.create_text_channel(name="管理者用", category=category, overwrites=moderator_overwrites)
        await general_channel.send(f"作成が完了しました")
        await moderator_channel.send(f"{build_request.sender.mention} 参加申請があった場合はこのチャンネルに通知されます。このチャンネルはこのカテゴリーの管理者にのみ表示されます。")

        guild_data = interaction.guild
        data.add_category(guild_data.id, category.id, moderator_channel.id, build_request.sender.id, new_role.id)
        
    
    @discord.ui.button(label="Deny", row=1, style=discord.ButtonStyle.red)
    async def deny_button_callback(self, button: discord.ui.Button ,interaction: discord.Interaction):
        message_id = interaction.message.id
        build_request = build_request_dict[message_id]
        build_request.deny(interaction.user)
        embed = build_request.get_embed()
        await build_request.sender.send("Build Request Denied", embed=embed)
        build_request_dict.pop(message_id)
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

@bot.slash_command(guild_ids=guild_ids)
async def join_request(ctx: discord.ApplicationContext, role: discord.Role):
    await ctx.respond(f"Join Request for {role.name} sent", ephemeral=True)
    category_data = data.get_category_with_role_id(ctx.guild_id, role.id)
    if not category_data:
        await ctx.respond("Category not found", ephemeral=True)
        return
    category_id = category_data["category"]
    owner_id = category_data["owner"]
    moderator_channel_id = category_data.get("moderator_channel", None)
    if not category_id or not moderator_channel_id or not owner_id:
        await ctx.respond("エラーが発生しました", ephemeral=True)
        return
    owner = bot.get_user(owner_id)
    moderator_channel = bot.get_channel(moderator_channel_id)
    await moderator_channel.send(f"{owner.mention}{ctx.author.display_name} さんが参加申請を送りました。", view=JoinRequestView())

@bot.slash_command(guild_ids=guild_ids)
async def set_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    data.set_channel(ctx.guild_id, channel.id)
    await ctx.respond(f"Channel set to {channel.id}")

@bot.slash_command(guild_ids=guild_ids)
async def test_send(ctx: discord.ApplicationContext, message: str):
    channel_id = data.get_channel(ctx.guild_id)
    if not channel_id:
        await ctx.respond("No channel set")
        return
    channel = bot.get_channel(channel_id)
    await channel.send(message)
    await ctx.respond("Message sent", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def save_data(ctx: discord.ApplicationContext):
    data.save()
    await ctx.respond("Data saved", ephemeral=True)

@bot.slash_command(guild_ids=guild_ids)
async def build_request(ctx: discord.ApplicationContext, name: str):
    channel_id = data.get_channel(ctx.guild_id)
    if not channel_id:
        await ctx.respond("No channel set")
        return
    channel = bot.get_channel(channel_id)
    view = BuildRequestView()
    message = await channel.send("loading")
    build_request = BuildRequest(message.id, name, ctx.author)
    await message.edit("", embed=build_request.get_embed(), view=view)
    build_request_dict[message.id] = build_request
    await ctx.respond(f"", embed=build_request.get_send_embed())

@bot.slash_command(guild_ids=guild_ids)
async def stop(ctx: discord.ApplicationContext):
    if ctx.author.id == 423662596533518358:
        await ctx.respond("Bot stopped", ephemeral=True)
        await bot.close()
    else:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)

data = Data_Storage()
bot.run(token)