# 🤖 MEE6 Bot - XBot Project

## 📁 هيكل الملفات

```
MEE6/
├── moderation/
│   ├── ban.py          → /ban - حظر عضو
│   ├── tempban.py      → /tempban - حظر مؤقت
│   ├── unban.py        → /unban - فك الحظر
│   ├── kick.py         → /kick - طرد عضو
│   ├── mute.py         → /mute و /unmute
│   └── moderation.py   → /clear, /slowmode, /warn, /unwarn, /infractions
├── levels/
│   └── levels.py       → /rank, /leaderboard + XP تلقائي
├── welcome/
│   └── welcome.py      → /setwelcome, /welcome-test, /goodbye-test
├── info/
│   └── info.py         → /user-info, /server-info, /avatar, /poll
├── automod/
│   └── automod.py      → /antilink, /antispam, /antibadwords
├── logs/
│   └── logs.py         → /setlogs + سجلات تلقائية
├── reaction_roles/
│   └── reaction_roles.py → /reactionrole
├── custom_commands/
│   └── custom_commands.py → /addcommand, /delcommand, /listcommands
├── auto_messages/
│   └── auto_messages.py → /automessage, /stopauto
└── main.py
```

## 🚀 تشغيل البوت
1. ضع التوكن في `main.py` مكان `TOKEN_HERE`
2. شغّل من مجلد XBot:
```bash
python MEE6/main.py
```
