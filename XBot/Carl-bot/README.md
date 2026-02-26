# 🤖 Carl-bot - XBot Project

## 📁 هيكل الملفات
```
Carl-bot/
├── moderation/
│   └── moderation.py   → ban, tempban, unban, kick, mute, unmute, warn, warnings, purge, slowmode, lock, unlock, nick, role
├── automod/
│   └── automod.py      → automod, filter-add, filter-remove, antispam, antilink
├── reaction_roles/
│   └── reaction_roles.py → rr-create, rr-add, rr-delete
├── info/
│   └── info.py         → userinfo, serverinfo, roleinfo, avatar, botinfo, help
├── logs/
│   └── logs.py         → setlogs + سجلات تلقائية كاملة
├── giveaway/
│   └── giveaway.py     → gstart, gend, greroll
├── tags/
│   └── tags.py         → tag-create, tag-edit, tag-delete, tag, tag-list
├── starboard/
│   └── starboard.py    → starboard-setup + نظام النجوم التلقائي
└── main.py
```

## 🚀 تشغيل البوت
1. ضع التوكن في `main.py` مكان `TOKEN_HERE`
2. شغّل من مجلد XBot:
```bash
python Carl-bot/main.py
```
