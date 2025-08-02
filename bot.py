import interactions
import os
from flask import Flask
from threading import Thread
import json

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot activo"

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    Thread(target=run).start()

keep_alive()

bot = interactions.Client(token=os.getenv("DISCORD_BOT_TOKEN"), intents=interactions.Intents.DEFAULT)

warn_data_file = "sanciones.json"
perm_data_file = "permisos.json"

if not os.path.exists(warn_data_file):
    with open(warn_data_file, "w") as f:
        json.dump({}, f)

if not os.path.exists(perm_data_file):
    with open(perm_data_file, "w") as f:
        json.dump({}, f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@bot.command()
@interactions.option()
async def setrole(ctx, rol: interactions.Role):
    if not ctx.author.guild_permissions.ADMINISTRATOR:
        await ctx.send("❌ Solo administradores pueden usar este comando.", ephemeral=True)
        return

    with open(perm_data_file) as f:
        permisos = json.load(f)
    permisos[str(ctx.guild.id)] = rol.id
    save_json(perm_data_file, permisos)
    await ctx.send(f"✅ El rol `{rol.name}` ahora puede usar `/warn`.")

@bot.command()
@interactions.option()
@interactions.option()
@interactions.option()
async def warn(ctx, staff: interactions.Member, razon: str, sancion: str):
    with open(perm_data_file) as f:
        permisos = json.load(f)
    rol_permitido = permisos.get(str(ctx.guild.id))
    if not ctx.author.guild_permissions.ADMINISTRATOR and (not rol_permitido or rol_permitido not in [r.id for r in ctx.author.roles]):
        await ctx.send("❌ No tenés permisos para usar este comando.", ephemeral=True)
        return

    with open(warn_data_file) as f:
        data = json.load(f)

    user_id = str(staff.id)
    data[user_id] = data.get(user_id, 0) + 1
    conteo = data[user_id]

    if conteo >= 3:
        mensaje = (
            f"- Nombre: {staff.mention}
"
            f"- Sanción: Warn 3/3 + descenso
"
            f"- Razón: {razon}"
        )
        data[user_id] = 0
    else:
        mensaje = (
            f"- Nombre: {staff.mention}
"
            f"- Sanción: Warn {conteo}/3
"
            f"- Razón: {razon}"
        )

    save_json(warn_data_file, data)
    await ctx.send(mensaje)

bot.start()