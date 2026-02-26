from flask import Flask, redirect, request, session, url_for
import requests, os

app = Flask(__name__)
app.secret_key = "xbot-secret-change-this"

# ضع هنا بيانات تطبيقك من Discord Developer Portal
CLIENT_ID = "1476448192328372466"
CLIENT_SECRET = "MnJz52ZKJcSrppuHYWS_fI7bbJP73Vvz"
REDIRECT_URI = "http://localhost:5000/callback"

DISCORD_API = "https://discord.com/api/v10"
OAUTH_URL = (
    f"https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=identify+guilds"
)

HTML_BASE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>XBot Dashboard</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0e0e1a; color:#e8e8f0; font-family:'Segoe UI',Arial,sans-serif; min-height:100vh; }}
nav {{ background:#16162a; padding:16px 32px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(124,92,191,0.2); }}
.logo {{ font-size:1.5rem; font-weight:800; color:#a07be0; }}
.logo span {{ color:#f5c842; }}
.user-info {{ display:flex; align-items:center; gap:10px; }}
.avatar {{ width:36px; height:36px; border-radius:50%; }}
.btn {{ padding:10px 22px; border-radius:8px; font-size:0.95rem; font-weight:600; text-decoration:none; border:none; cursor:pointer; transition:all .2s; display:inline-flex; align-items:center; gap:8px; }}
.btn-discord {{ background:#5865F2; color:#fff; }}
.btn-discord:hover {{ background:#4752c4; transform:translateY(-2px); }}
.btn-logout {{ background:rgba(224,82,82,0.15); color:#e05252; border:1px solid rgba(224,82,82,0.3); }}
.btn-back {{ background:rgba(124,92,191,0.15); color:#a07be0; border:1px solid rgba(124,92,191,0.3); }}
.hero {{ text-align:center; padding:80px 20px 60px; }}
.hero h1 {{ font-size:2.8rem; font-weight:900; margin-bottom:14px; }}
.hero h1 span {{ color:#a07be0; }}
.hero p {{ color:#9090b0; font-size:1.1rem; margin-bottom:32px; }}
.container {{ max-width:1000px; margin:0 auto; padding:40px 20px 60px; }}
.section-title {{ font-size:1.3rem; font-weight:700; margin-bottom:20px; color:#a07be0; }}
.servers-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; }}
.server-card {{ background:#16162a; border:1px solid rgba(255,255,255,0.07); border-radius:14px; padding:20px; text-align:center; transition:all .2s; text-decoration:none; color:inherit; display:block; }}
.server-card:hover {{ border-color:rgba(124,92,191,0.5); transform:translateY(-3px); background:#1e1e35; }}
.server-icon {{ width:64px; height:64px; border-radius:16px; margin:0 auto 12px; object-fit:cover; display:block; }}
.server-icon-placeholder {{ width:64px; height:64px; border-radius:16px; margin:0 auto 12px; background:linear-gradient(135deg,#7c5cbf,#a07be0); display:flex; align-items:center; justify-content:center; font-size:1.6rem; font-weight:800; color:#fff; }}
.server-name {{ font-weight:700; font-size:0.95rem; margin-bottom:8px; }}
.badge {{ display:inline-block; padding:3px 12px; border-radius:10px; font-size:0.75rem; font-weight:600; }}
.badge-has {{ background:rgba(67,212,122,0.15); color:#43d47a; }}
.badge-no {{ background:rgba(144,144,176,0.15); color:#9090b0; }}
.info-card {{ background:#16162a; border-radius:14px; padding:28px; border:1px solid rgba(255,255,255,0.07); }}
footer {{ text-align:center; padding:30px; color:#9090b0; font-size:0.85rem; border-top:1px solid rgba(255,255,255,0.05); margin-top:auto; }}
code {{ background:#0e0e1a; padding:2px 8px; border-radius:5px; color:#a07be0; font-family:monospace; }}
</style>
</head>
<body>
{content}
<footer>⚡ XBot Dashboard — مجاني 100%</footer>
</body>
</html>
"""

@app.route("/")
def index():
    user = session.get("user")
    if user:
        avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else "https://cdn.discordapp.com/embed/avatars/0.png"
        nav = f"""
        <nav>
          <div class="logo">⚡ <span>X</span>Bot</div>
          <div class="user-info">
            <img class="avatar" src="{avatar_url}">
            <span>{user['username']}</span>
            <a href="/logout" class="btn btn-logout">خروج</a>
          </div>
        </nav>"""
        content = nav + f"""
        <div class="container">
          <div class="section-title">🖥️ سيرفراتك</div>
          <div class="servers-grid" id="servers">
            <p style="color:#9090b0;">جاري تحميل السيرفرات...</p>
          </div>
        </div>
        <script>
        fetch('/api/guilds').then(r=>r.json()).then(guilds=>{{
          const grid = document.getElementById('servers');
          if(!guilds.length){{
            grid.innerHTML='<p style="color:#9090b0;grid-column:1/-1;">ما عندك سيرفرات أو البوت ما مضاف</p>';
            return;
          }}
          grid.innerHTML = guilds.map(g => {{
            const icon = g.icon
              ? `<img class="server-icon" src="https://cdn.discordapp.com/icons/${{g.id}}/${{g.icon}}.png">`
              : `<div class="server-icon-placeholder">${{g.name[0]}}</div>`;
            const badge = g.bot_in
              ? `<span class="badge badge-has">✅ البوت موجود</span>`
              : `<span class="badge badge-no">➕ أضف البوت</span>`;
            const href = g.bot_in
              ? `/dashboard/${{g.id}}`
              : `https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&scope=bot&permissions=8&guild_id=${{g.id}}`;
            return `<a class="server-card" href="${{href}}">${{icon}}<div class="server-name">${{g.name}}</div>${{badge}}</a>`;
          }}).join('');
        }});
        </script>"""
    else:
        content = """
        <nav><div class="logo">⚡ <span>X</span>Bot</div></nav>
        <div class="hero">
          <h1>مرحباً في <span>XBot</span> Dashboard</h1>
          <p>سجّل دخولك بحساب Discord وشوف سيرفراتك وتحكم في البوت</p>
          <a href="/login" class="btn btn-discord">
            <svg width="20" height="20" viewBox="0 0 71 55" fill="white"><path d="M60.1 4.9A58.5 58.5 0 0 0 45.6.4a.2.2 0 0 0-.2.1 40.7 40.7 0 0 0-1.8 3.7 54 54 0 0 0-16.2 0A37.6 37.6 0 0 0 25.6.5a.2.2 0 0 0-.2-.1A58.4 58.4 0 0 0 10.9 4.9a.2.2 0 0 0-.1.1C1.6 18.1-.9 31 .3 43.7a.2.2 0 0 0 .1.1 58.8 58.8 0 0 0 17.7 8.9.2.2 0 0 0 .2-.1 42 42 0 0 0 3.6-5.9.2.2 0 0 0-.1-.3 38.7 38.7 0 0 1-5.5-2.6.2.2 0 0 1 0-.4l1.1-.8a.2.2 0 0 1 .2 0c11.5 5.3 24 5.3 35.4 0a.2.2 0 0 1 .2 0l1.1.8a.2.2 0 0 1 0 .4 36.2 36.2 0 0 1-5.5 2.6.2.2 0 0 0-.1.3 47.1 47.1 0 0 0 3.6 5.9.2.2 0 0 0 .2.1 58.7 58.7 0 0 0 17.7-8.9.2.2 0 0 0 .1-.1c1.5-15.2-2.5-28-10.5-39.6a.2.2 0 0 0-.1-.2zM23.7 36c-3.5 0-6.4-3.2-6.4-7.1s2.8-7.1 6.4-7.1c3.6 0 6.5 3.2 6.4 7.1 0 3.9-2.8 7.1-6.4 7.1zm23.6 0c-3.5 0-6.4-3.2-6.4-7.1s2.8-7.1 6.4-7.1c3.6 0 6.5 3.2 6.4 7.1 0 3.9-2.8 7.1-6.4 7.1z"/></svg>
            تسجيل الدخول بـ Discord
          </a>
        </div>"""
    return HTML_BASE.format(content=content)

@app.route("/login")
def login():
    return redirect(OAUTH_URL)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect("/")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    r = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    tokens = r.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return "خطأ في تسجيل الدخول — تأكد من CLIENT_ID و CLIENT_SECRET", 400
    headers = {"Authorization": f"Bearer {access_token}"}
    user = requests.get(f"{DISCORD_API}/users/@me", headers=headers).json()
    session["user"] = user
    session["access_token"] = access_token
    return redirect("/")

@app.route("/api/guilds")
def api_guilds():
    token = session.get("access_token")
    if not token:
        return [], 401
    headers = {"Authorization": f"Bearer {token}"}
    guilds = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers).json()
    if not isinstance(guilds, list):
        return [], 200
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    bot_headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    bot_guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=bot_headers)
    bot_guild_ids = set()
    if bot_guilds_r.ok:
        bot_guild_ids = {g["id"] for g in bot_guilds_r.json()}
    result = []
    for g in guilds:
        if int(g.get("permissions", 0)) & 0x20 or g.get("owner"):
            g["bot_in"] = g["id"] in bot_guild_ids
            result.append(g)
    from flask import jsonify
    return jsonify(result)

@app.route("/dashboard/<guild_id>")
def dashboard(guild_id):
    user = session.get("user")
    if not user:
        return redirect("/login")
    avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else "https://cdn.discordapp.com/embed/avatars/0.png"
    nav = f"""
    <nav>
      <div class="logo">⚡ <span>X</span>Bot</div>
      <div class="user-info">
        <img class="avatar" src="{avatar_url}">
        <span>{user['username']}</span>
        <a href="/" class="btn btn-back">← رجوع</a>
      </div>
    </nav>"""
    content = nav + f"""
    <div class="container">
      <div class="section-title">⚙️ إعدادات السيرفر</div>
      <div class="info-card">
        <p style="color:#9090b0;margin-bottom:12px;">🚧 صفحة الإعدادات قيد التطوير — قريباً تتحكم في كل إعدادات البوت من هنا!</p>
        <p style="color:#9090b0;">ID السيرفر: <code>{guild_id}</code></p>
      </div>
    </div>"""
    return HTML_BASE.format(content=content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
