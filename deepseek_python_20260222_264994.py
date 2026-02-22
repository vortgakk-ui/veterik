import telebot
from telebot import types
import random
import time
import json
import os
from threading import Timer, Lock, Thread
from datetime import datetime, timedelta
import string

# Токен бота
TOKEN = '8069008534:AAGxpJM95uwhM6t1BVdZeVh5wdDfauEaHbg'
bot = telebot.TeleBot(TOKEN)

# Владелец и канал
OWNER_USERNAME = '@kyniks'
CHANNEL_USERNAME = '@werdoxz_wiinere'
CHAT_LINK = 'https://t.me/+B7u5OmPsako4MTAy'

# Файлы для хранения данных
DATA_FILE = 'bot_data.json'
USERNAME_CACHE_FILE = 'username_cache.json'
PROMO_FILE = 'promocodes.json'
MARKET_FILE = 'market_data.json'
BUSINESS_FILE = 'business_data.json'
CLAN_FILE = 'clan_data.json'
ACHIEVEMENTS_FILE = 'achievements.json'
DUEL_FILE = 'duel_data.json'
LOGS_FILE = 'logs_data.json'
QUESTS_FILE = 'quests_data.json'
EVENT_FILE = 'event_data.json'
CASES_FILE = 'cases_data.json'
ORDERS_FILE = 'orders.json'          # для P2P ордеров
CHEQUES_FILE = 'cheques.json'         # для чековой книжки

# Максимальная ставка
MAX_BET = 100000000  # 100 млн (100кк)
GAME_TIMEOUT = 300
ADMIN_PASSWORD = '18472843'

# Банковские параметры
BANK_INTEREST_RATE = 0.001
BANK_INTEREST_INTERVAL = 24 * 60 * 60

users = {}
username_cache = {}
game_timers = {}
crash_update_timers = {}
crash_locks = {}
admin_users = set()
promocodes = {}
used_promocodes = {}
logs = {}

# ====================== СИСТЕМА КЕЙСОВ ======================
CASES = {
    'case1': {
        'name': '😁лол😁',
        'price': 3000,
        'min_win': 1000,
        'max_win': 5000,
        'icon': '📦'
    },
    'case2': {
        'name': '🎮лотус🎮',
        'price': 10000,
        'min_win': 7500,
        'max_win': 15000,
        'icon': '🎮'
    },
    'case3': {
        'name': '💫люкс кейс💫',
        'price': 50000,
        'min_win': 35000,
        'max_win': 65000,
        'icon': '💫'
    },
    'case4': {
        'name': '💎Платинум💍',
        'price': 200000,
        'min_win': 175000,
        'max_win': 250000,
        'icon': '💎'
    },
    'case5': {
        'name': '💫специальный кейс👾',
        'price': 1000000,
        'min_win': 750000,
        'max_win': 1250000,
        'icon': '👾'
    },
    'case6': {
        'name': '🎉инвентовый🎊',
        'price': 0,
        'min_win': 12500,
        'max_win': 75000,
        'icon': '🎉'
    }
}

user_cases = {}

# ====================== СИСТЕМА ЕЖЕДНЕВНЫХ ЗАДАНИЙ ======================
DAILY_QUESTS = {
    'play_3_games': {
        'name': '🎮 Игрок',
        'desc': 'Сыграть 3 любые игры',
        'reward': 5000,
        'target': 3,
        'icon': '🎲',
        'type': 'play'
    },
    'win_2_games': {
        'name': '🏆 Победитель',
        'desc': 'Выиграть 2 игры',
        'reward': 8000,
        'target': 2,
        'icon': '🏅',
        'type': 'win'
    },
    'earn_15000': {
        'name': '💰 Добытчик',
        'desc': 'Заработать 15,000 кредиксов',
        'reward': 12000,
        'target': 15000,
        'icon': '💵',
        'type': 'earn'
    },
    'play_crash_2': {
        'name': '🚀 Космонавт',
        'desc': 'Сыграть в Краш 2 раза',
        'reward': 6000,
        'target': 2,
        'icon': '🚀',
        'type': 'crash'
    },
    'play_mines_2': {
        'name': '💣 Сапёр',
        'desc': 'Сыграть в Мины 2 раза',
        'reward': 6000,
        'target': 2,
        'icon': '💣',
        'type': 'mines'
    },
    'play_slots_3': {
        'name': '🎰 Однорукий',
        'desc': 'Сыграть в Слоты 3 раза',
        'reward': 7000,
        'target': 3,
        'icon': '🎰',
        'type': 'slots'
    },
    'play_blackjack_2': {
        'name': '🃏 Картёжник',
        'desc': 'Сыграть в Очко 2 раза',
        'reward': 6500,
        'target': 2,
        'icon': '🃏',
        'type': 'blackjack'
    },
    'play_roulette_3': {
        'name': '🎰 Рулеточник',
        'desc': 'Сыграть в Рулетку 3 раза',
        'reward': 7500,
        'target': 3,
        'icon': '🎯',
        'type': 'roulette'
    },
    'play_tower_2': {
        'name': '🏰 Скалолаз',
        'desc': 'Сыграть в Башню 2 раза',
        'reward': 5500,
        'target': 2,
        'icon': '🏰',
        'type': 'tower'
    },
    'play_dice_2': {
        'name': '🎲 Кости',
        'desc': 'Сыграть в Кости 2 раза',
        'reward': 5000,
        'target': 2,
        'icon': '🎲',
        'type': 'dice'
    }
}

# ====================== СИСТЕМА ИВЕНТОВ ======================
RELEASE_EVENT = {
    'active': True,
    'name': '🎉 РЕЛИЗ БОТА!',
    'start_time': time.time(),
    'end_time': time.time() + 7 * 24 * 60 * 60,
    'multiplier': 1.5,
    'bonus_quest_reward': 2,
    'special_shop': {
        'event_beaver': {
            'name': '🎉 Релизный бобёр',
            'price': 50000,
            'total': 50,
            'sold': 0,
            'rarity': 'Ивентовый',
            'description': 'Особый бобёр в честь релиза!',
            'bonus': '+50% к доходу от ивентов'
        }
    }
}

event_data = {
    'active': True,
    'participants': {},
    'leaderboard': [],
    'last_update': time.time()
}

# ====================== ДОСТИЖЕНИЯ ======================
achievements = {
    'first_game': {'name': '🎮 Первый шаг', 'desc': 'Сыграть первую игру', 'reward': 1000},
    'millionaire': {'name': '💰 Миллионер', 'desc': 'Накопить 1,000,000 кредиксов', 'reward': 50000},
    'beaver_collector': {'name': '🦫 Коллекционер', 'desc': 'Собрать всех видов бобров', 'reward': 100000},
    'high_roller': {'name': '🎲 Хайроллер', 'desc': 'Сделать ставку 100,000', 'reward': 25000},
    'lucky_winner': {'name': '🍀 Счастливчик', 'desc': 'Выиграть 10 игр подряд', 'reward': 50000},
    'clan_leader': {'name': '👑 Лидер клана', 'desc': 'Создать клан 5 уровня', 'reward': 200000},
    'business_tycoon': {'name': '💼 Магнат', 'desc': 'Купить все виды бизнесов', 'reward': 150000},
    'duel_master': {'name': '⚔️ Мастер дуэлей', 'desc': 'Выиграть 50 дуэлей', 'reward': 75000},
    'daily_streak': {'name': '📅 Марафонец', 'desc': 'Получить ежедневный бонус 30 дней подряд', 'reward': 200000},
    'jackpot_winner': {'name': '🎰 Джекпот', 'desc': 'Сорвать джекпот', 'reward': 250000},
    'referral_master': {'name': '🤝 Реферал', 'desc': 'Пригласить 10 друзей', 'reward': 100000},
    'game_master': {'name': '🎯 Мастер игр', 'desc': 'Сыграть во все игры', 'reward': 100000},
    'event_participant': {'name': '🎉 Участник ивента', 'desc': 'Принять участие в ивенте', 'reward': 15000},
    'quest_master': {'name': '📋 Квестер', 'desc': 'Выполнить 50 заданий', 'reward': 75000}
}

user_achievements = {}

# Ежедневный бонус (заменён на новый)
daily_reward = {}

# Джекпот
jackpot = {
    'total': 0,
    'last_winner': None,
    'last_win_time': None,
    'history': []
}

# Дуэли
duels = {}

# Кланы
clans = {}

CLAN_LEVELS = {
    1: {'exp_needed': 1000, 'max_members': 5, 'bonus': 1.05},
    2: {'exp_needed': 5000, 'max_members': 10, 'bonus': 1.10},
    3: {'exp_needed': 15000, 'max_members': 15, 'bonus': 1.15},
    4: {'exp_needed': 30000, 'max_members': 20, 'bonus': 1.20},
    5: {'exp_needed': 50000, 'max_members': 25, 'bonus': 1.30}
}

# Бизнесы
businesses = {}

BUSINESSES_DATA = {
    'lime': {
        'name': '🍋 Ларёк с лимонадом',
        'price': 5000,
        'income': 500,
        'cooldown': 3600,
        'max_level': 10,
        'upgrade_price': 3000,
        'image': '🏪'
    },
    'kiosk': {
        'name': '📰 Газетный киоск',
        'price': 15000,
        'income': 2000,
        'cooldown': 7200,
        'max_level': 10,
        'upgrade_price': 8000,
        'image': '🏬'
    },
    'cafe': {
        'name': '☕ Кафе',
        'price': 50000,
        'income': 8000,
        'cooldown': 14400,
        'max_level': 10,
        'upgrade_price': 25000,
        'image': '🏨'
    },
    'shop': {
        'name': '🛒 Магазин',
        'price': 150000,
        'income': 30000,
        'cooldown': 28800,
        'max_level': 10,
        'upgrade_price': 75000,
        'image': '🏪'
    },
    'restaurant': {
        'name': '🍽️ Ресторан',
        'price': 500000,
        'income': 120000,
        'cooldown': 43200,
        'max_level': 10,
        'upgrade_price': 250000,
        'image': '🍷'
    },
    'hotel': {
        'name': '🏨 Отель',
        'price': 1000000,
        'income': 300000,
        'cooldown': 86400,
        'max_level': 10,
        'upgrade_price': 500000,
        'image': '🏰'
    }
}

# Маркет бобров
BEAVERS_DATA = {
    'kunos': {
        'name': '💥кунос💥',
        'price': 100000,
        'total': 100,
        'sold': 0,
        'rarity': 'Обычная',
        'description': '💫фон: standart bobri💫',
        'global_mult': 1.2
    },
    'luxer': {
        'name': '💫люксер💫',
        'price': 250000,
        'total': 150,
        'sold': 0,
        'rarity': 'lvbober',
        'description': '💫фон: special bobri💫',
        'global_mult': 1.3
    },
    'platinumi': {
        'name': '💎платинумик💎',
        'price': 500000,
        'total': 75,
        'sold': 0,
        'rarity': 'platinum',
        'description': '💫фон: Platinum 💫',
        'global_mult': 1.4
    },
    'legend': {
        'name': '🎉легенда🎉',
        'price': 1000000,
        'total': 25,
        'sold': 0,
        'rarity': 'legendary',
        'description': '💫фон: lucky 💫',
        'global_mult': 1.5
    },
    'special': {
        'name': '🎮СПЕЦИАЛЬНЫЙ🎮',
        'price': 15000000,
        'total': 10,
        'sold': 0,
        'rarity': 'LUX',
        'description': '💫фон: special 💫',
        'global_mult': 1.75
    }
}

if RELEASE_EVENT['active']:
    BEAVERS_DATA['event_beaver'] = RELEASE_EVENT['special_shop']['event_beaver']

# Коэффициенты для игр
TOWER_MULTIPLIERS = {
    1: 1.3,
    2: 2.1,
    3: 3.7,
    4: 4.55,
    5: 5.4
}

PYRAMID_MULTIPLIER = 1.5
PYRAMID_CELLS = 10  # ИЗМЕНЕНО с 4 на 10

FOOTBALL_MULTIPLIER = 2.0
BASKETBALL_MULTIPLIER = 2.0

HILO_RISKS = {
    'low': {'mult': 1.5, 'win_chance': 0.7},
    'medium': {'mult': 2.5, 'win_chance': 0.4},
    'high': {'mult': 5.0, 'win_chance': 0.2}
}

BLACKJACK_MULTIPLIER = 1.87
SLOTS_SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '7️⃣', 'BAR']
SLOTS_PAYOUTS = {
    ('BAR', 'BAR', 'BAR'): 10,
    ('7️⃣', '7️⃣', '7️⃣'): 7,
    ('🍇', '🍇', '🍇'): 5,
    ('🍊', '🍊', '🍊'): 3,
    ('🍋', '🍋', '🍋'): 2,
    ('🍒', '🍒', '🍒'): 1.5
}

ROULETTE_NUMBERS = list(range(0, 37))
RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

ROULETTE_MULTIPLIERS = {
    'straight': 36,
    'red': 2,
    'black': 2,
    'color': 2,
    'even': 2,
    'odd': 2,
    '1-18': 2,
    '19-36': 2,
    'dozen': 3
}

MINES_FIELD_SIZE = 5
MINES_MULTIPLIERS = {
    1: {1: 1.05, 2: 1.10, 3: 1.15, 4: 1.20, 5: 1.25, 6: 1.30, 7: 1.35, 8: 1.40, 9: 1.45, 10: 1.50,
        11: 1.55, 12: 1.60, 13: 1.65, 14: 1.70, 15: 1.75, 16: 1.80, 17: 1.85, 18: 1.90, 19: 1.95, 20: 2.00,
        21: 2.05, 22: 2.10, 23: 2.15, 24: 2.20},
    2: {1: 1.10, 2: 1.20, 3: 1.30, 4: 1.40, 5: 1.50, 6: 1.60, 7: 1.70, 8: 1.80, 9: 1.90, 10: 2.00,
        11: 2.10, 12: 2.20, 13: 2.30, 14: 2.40, 15: 2.50, 16: 2.60, 17: 2.70, 18: 2.80, 19: 2.90, 20: 3.00,
        21: 3.10, 22: 3.20, 23: 3.30},
    3: {1: 1.15, 2: 1.30, 3: 1.45, 4: 1.60, 5: 1.75, 6: 1.90, 7: 2.05, 8: 2.20, 9: 2.35, 10: 2.50,
        11: 2.65, 12: 2.80, 13: 2.95, 14: 3.10, 15: 3.25, 16: 3.40, 17: 3.55, 18: 3.70, 19: 3.85, 20: 4.00,
        21: 4.15, 22: 4.30},
    4: {1: 1.20, 2: 1.40, 3: 1.60, 4: 1.80, 5: 2.00, 6: 2.20, 7: 2.40, 8: 2.60, 9: 2.80, 10: 3.00,
        11: 3.20, 12: 3.40, 13: 3.60, 14: 3.80, 15: 4.00, 16: 4.20, 17: 4.40, 18: 4.60, 19: 4.80, 20: 5.00,
        21: 5.20},
    5: {1: 1.25, 2: 1.50, 3: 1.75, 4: 2.00, 5: 2.25, 6: 2.50, 7: 2.75, 8: 3.00, 9: 3.25, 10: 3.50,
        11: 3.75, 12: 4.00, 13: 4.25, 14: 4.50, 15: 4.75, 16: 5.00, 17: 5.25, 18: 5.50, 19: 5.75, 20: 6.00}
}

user_quests = {}

# ====================== НОВЫЕ СИСТЕМЫ ======================

# Донат-валюта KRDS уже добавлена в структуру пользователя
# P2P обменник
orders = {}  # order_id -> order
next_order_id = 1
TREASURY_RATE = 3000  # начальный курс казны, будет обновляться
treasury_lock = Lock()

# Чеки
cheques = {}  # code -> cheque_data

# ====================== ФУНКЦИИ ЗАГРУЗКИ/СОХРАНЕНИЯ ======================
def safe_json_load(file_path, default_value=None):
    if default_value is None:
        default_value = {} if not file_path.endswith('.json') else {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    os.rename(file_path, file_path + '.bak')
                    return default_value
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            if os.path.exists(file_path):
                os.rename(file_path, file_path + '.error.bak')
            return default_value
    return default_value

def load_data():
    global users, username_cache, promocodes, used_promocodes, clans, businesses
    global user_achievements, daily_reward, jackpot, duels, logs, user_quests, event_data
    global user_cases, orders, next_order_id, cheques, TREASURY_RATE

    users_data = safe_json_load(DATA_FILE, {})
    if users_data:
        users = {str(k): v for k, v in users_data.items()}
        for uid in users:
            if 'banned' not in users[uid]:
                users[uid]['banned'] = False
            if 'bank' not in users[uid]:
                users[uid]['bank'] = {'balance': 0, 'last_interest': time.time(), 'history': []}
            if 'beavers' not in users[uid]:
                users[uid]['beavers'] = {}
            if 'used_promos' not in users[uid]:
                users[uid]['used_promos'] = []
            if 'clan' not in users[uid]:
                users[uid]['clan'] = None
            if 'total_wins' not in users[uid]:
                users[uid]['total_wins'] = 0
            if 'total_losses' not in users[uid]:
                users[uid]['total_losses'] = 0
            if 'total_bets' not in users[uid]:
                users[uid]['total_bets'] = 0
            if 'games_played' not in users[uid]:
                users[uid]['games_played'] = 0
            if 'win_streak' not in users[uid]:
                users[uid]['win_streak'] = 0
            if 'max_win_streak' not in users[uid]:
                users[uid]['max_win_streak'] = 0
            if 'total_lost' not in users[uid]:
                users[uid]['total_lost'] = 0
            if 'quests_completed' not in users[uid]:
                users[uid]['quests_completed'] = 0
            if 'event_points' not in users[uid]:
                users[uid]['event_points'] = 0
            # Новые поля
            if 'krds_balance' not in users[uid]:
                users[uid]['krds_balance'] = 0
            if 'game_history' not in users[uid]:
                users[uid]['game_history'] = []
            if 'daily_last_claim' not in users[uid]:
                users[uid]['daily_last_claim'] = 0
            if 'daily_streak' not in users[uid]:
                users[uid]['daily_streak'] = 0
            # Добавлено поле для отслеживания времени открытия ивентового кейса
            if 'last_case6_open' not in users[uid]:
                users[uid]['last_case6_open'] = 0

    username_cache = safe_json_load(USERNAME_CACHE_FILE, {})
    promocodes = safe_json_load(PROMO_FILE, {})

    market_data = safe_json_load(MARKET_FILE, {})
    if market_data and 'beavers_sold' in market_data:
        for beaver_id, data in market_data['beavers_sold'].items():
            if beaver_id in BEAVERS_DATA:
                BEAVERS_DATA[beaver_id]['sold'] = data

    clans = safe_json_load(CLAN_FILE, {})
    businesses = safe_json_load(BUSINESS_FILE, {})
    user_achievements = safe_json_load(ACHIEVEMENTS_FILE, {})
    daily_reward = safe_json_load('daily_reward.json', {})

    jackpot_data = safe_json_load('jackpot.json', {'total': 0, 'last_winner': None, 'last_win_time': None, 'history': []})
    if jackpot_data:
        jackpot.update(jackpot_data)

    duels = safe_json_load(DUEL_FILE, {})
    logs = safe_json_load(LOGS_FILE, {})
    user_quests = safe_json_load(QUESTS_FILE, {})

    event_data = safe_json_load(EVENT_FILE, {
        'active': RELEASE_EVENT['active'],
        'participants': {},
        'leaderboard': [],
        'last_update': time.time()
    })

    user_cases = safe_json_load(CASES_FILE, {})

    # Загрузка ордеров
    orders_data = safe_json_load(ORDERS_FILE, {})
    if orders_data:
        orders = orders_data.get('orders', {})
        next_order_id = orders_data.get('next_id', 1)
        TREASURY_RATE = orders_data.get('treasury_rate', 3000)

    # Загрузка чеков
    cheques = safe_json_load(CHEQUES_FILE, {})

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    with open(USERNAME_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(username_cache, f, ensure_ascii=False, indent=2)
    with open(PROMO_FILE, 'w', encoding='utf-8') as f:
        json.dump(promocodes, f, ensure_ascii=False, indent=2)
    with open(CLAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(clans, f, ensure_ascii=False, indent=2)
    with open(BUSINESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(businesses, f, ensure_ascii=False, indent=2)
    with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_achievements, f, ensure_ascii=False, indent=2)
    with open('daily_reward.json', 'w', encoding='utf-8') as f:
        json.dump(daily_reward, f, ensure_ascii=False, indent=2)
    with open('jackpot.json', 'w', encoding='utf-8') as f:
        json.dump(jackpot, f, ensure_ascii=False, indent=2)
    with open(DUEL_FILE, 'w', encoding='utf-8') as f:
        json.dump(duels, f, ensure_ascii=False, indent=2)
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    market_data = {
        'beavers_sold': {bid: BEAVERS_DATA[bid]['sold'] for bid in BEAVERS_DATA}
    }
    with open(MARKET_FILE, 'w', encoding='utf-8') as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)

    with open(QUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_quests, f, ensure_ascii=False, indent=2)
    with open(EVENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(event_data, f, ensure_ascii=False, indent=2)
    with open(CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_cases, f, ensure_ascii=False, indent=2)

    # Сохранение ордеров
    orders_data = {
        'orders': orders,
        'next_id': next_order_id,
        'treasury_rate': TREASURY_RATE
    }
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders_data, f, ensure_ascii=False, indent=2)

    # Сохранение чеков
    with open(CHEQUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cheques, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            'balance': 1000,
            'krds_balance': 0,
            'game': None,
            'referrals': 0,
            'referrer': None,
            'banned': False,
            'bank': {'balance': 0, 'last_interest': time.time(), 'history': []},
            'beavers': {},
            'used_promos': [],
            'clan': None,
            'total_wins': 0,
            'total_losses': 0,
            'total_bets': 0,
            'games_played': 0,
            'win_streak': 0,
            'max_win_streak': 0,
            'total_lost': 0,
            'quests_completed': 0,
            'event_points': 0,
            'game_history': [],
            'daily_last_claim': 0,
            'daily_streak': 0,
            'last_case6_open': 0   # Добавлено поле
        }
        save_data()
    # Если у старых пользователей нет новых полей
    if 'krds_balance' not in users[user_id]:
        users[user_id]['krds_balance'] = 0
    if 'game_history' not in users[user_id]:
        users[user_id]['game_history'] = []
    if 'daily_last_claim' not in users[user_id]:
        users[user_id]['daily_last_claim'] = 0
        users[user_id]['daily_streak'] = 0
    if 'last_case6_open' not in users[user_id]:
        users[user_id]['last_case6_open'] = 0
    return users[user_id]

def is_banned(user_id):
    user = get_user(user_id)
    return user.get('banned', False)

def is_admin(user_id):
    return str(user_id) in admin_users

def update_username_cache(user_id, username):
    if username:
        username_cache[username.lower()] = str(user_id)
        save_data()

def set_game_timer(user_id):
    user_id = str(user_id)
    if user_id in game_timers:
        game_timers[user_id].cancel()
    timer = Timer(GAME_TIMEOUT, game_timeout, [user_id])
    timer.daemon = True
    game_timers[user_id] = timer
    timer.start()

def game_timeout(user_id):
    try:
        user_id = str(user_id)
        if user_id in crash_update_timers:
            crash_update_timers[user_id].cancel()
            del crash_update_timers[user_id]
        if user_id in users and users[user_id]['game'] is not None:
            game = users[user_id]['game']
            chat_id = game.get('chat_id', int(user_id))
            if 'bet' in game:
                users[user_id]['balance'] += game['bet']
            users[user_id]['game'] = None
            save_data()
            bot.send_message(chat_id, 
                           "⏰ Время игры истекло. Ставка возвращена.",
                           reply_markup=main_menu_keyboard())
    except Exception as e:
        print(f"Ошибка при таймауте игры: {e}")

def clear_game(user_id):
    user_id = str(user_id)
    if user_id in game_timers:
        game_timers[user_id].cancel()
        del game_timers[user_id]
    if user_id in crash_update_timers:
        crash_update_timers[user_id].cancel()
        del crash_update_timers[user_id]
    if user_id in users:
        users[user_id]['game'] = None
    save_data()

def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('🏰 Башня'),
        types.KeyboardButton('💣 Мины'),
        types.KeyboardButton('🎰 Джекпот'),
        types.KeyboardButton('⚫️⚪️ Фишки'),
        types.KeyboardButton('🎲 X2/X3/X5'),
        types.KeyboardButton('🔫 Русская рулетка'),
        types.KeyboardButton('🃏 Очко (21)'),
        types.KeyboardButton('🚀 Краш'),
        types.KeyboardButton('🎰 Слоты'),
        types.KeyboardButton('🎲 Кости'),
        types.KeyboardButton('🎰 РУЛЕТКА'),
        types.KeyboardButton('⚽ Футбол'),
        types.KeyboardButton('📈 Хило'),
        types.KeyboardButton('🏀 Баскетбол'),
        types.KeyboardButton('🔺 Пирамида'),
        types.KeyboardButton('📦 Кейсы')
    )
    return markup

def parse_bet(bet_str):
    try:
        bet_str = bet_str.lower().strip()
        if 'кк' in bet_str:
            bet_str = bet_str.replace('кк', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000000)
        elif 'к' in bet_str:
            bet_str = bet_str.replace('к', '')
            if bet_str == '':
                bet_str = '1'
            return int(float(bet_str) * 1000)
        else:
            return int(bet_str)
    except:
        return None

# ====================== ФУНКЦИИ ДЛЯ ИСТОРИИ ИГР ======================
def add_game_history(user_id, game_type, bet, win_amount, result):
    user = get_user(user_id)
    history = user.get('game_history', [])
    entry = {
        'time': time.time(),
        'game': game_type,
        'bet': bet,
        'win': win_amount,
        'result': result  # 'win', 'lose', 'draw'
    }
    history.insert(0, entry)
    # Оставляем только последние 20 записей
    user['game_history'] = history[:20]
    save_data()

# ====================== ИГРЫ ======================

def start_football_game(message, bet, choice):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'football')
    result = random.choice(['гол', 'мимо'])
    emoji = '⚽'
    win_mult = get_global_multiplier(user_id) * get_event_multiplier()
    if choice == result:
        win = int(bet * FOOTBALL_MULTIPLIER * win_mult)
        user['balance'] += win
        user['total_wins'] += 1
        user['win_streak'] += 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'football', win)
        result_text = f"{emoji} ГОЛ! Ты угадал!\n💰 Выигрыш: {win} (x{FOOTBALL_MULTIPLIER})"
        add_game_history(user_id, '⚽ Футбол', bet, win, 'win')
    else:
        result_text = f"{emoji} МИМО! Ты не угадал.\n💰 Проигрыш: {bet}"
        user['total_losses'] += 1
        user['win_streak'] = 0
        user['total_lost'] += bet
        update_event_stats(user_id, 'football', 0)
        add_game_history(user_id, '⚽ Футбол', bet, 0, 'lose')
    user['max_win_streak'] = max(user['max_win_streak'], user['win_streak'])
    save_data()
    result_text += f"\n💰 Баланс: {user['balance']}"
    bot.send_message(message.chat.id, result_text)
    clear_game(user_id)

def start_basketball_game(message, bet, choice):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'basketball')
    result = random.choice(['гол', 'мимо'])
    emoji = '🏀'
    win_mult = get_global_multiplier(user_id) * get_event_multiplier()
    if choice == result:
        win = int(bet * BASKETBALL_MULTIPLIER * win_mult)
        user['balance'] += win
        user['total_wins'] += 1
        user['win_streak'] += 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'basketball', win)
        result_text = f"{emoji} ПОПАДАНИЕ! Ты угадал!\n💰 Выигрыш: {win} (x{BASKETBALL_MULTIPLIER})"
        add_game_history(user_id, '🏀 Баскетбол', bet, win, 'win')
    else:
        result_text = f"{emoji} ПРОМАХ! Ты не угадал.\n💰 Проигрыш: {bet}"
        user['total_losses'] += 1
        user['win_streak'] = 0
        user['total_lost'] += bet
        update_event_stats(user_id, 'basketball', 0)
        add_game_history(user_id, '🏀 Баскетбол', bet, 0, 'lose')
    user['max_win_streak'] = max(user['max_win_streak'], user['win_streak'])
    save_data()
    result_text += f"\n💰 Баланс: {user['balance']}"
    bot.send_message(message.chat.id, result_text)
    clear_game(user_id)

def start_hilo_game(message, bet, risk):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'hilo')
    risk_data = HILO_RISKS[risk]
    if random.random() < risk_data['win_chance']:
        win = int(bet * risk_data['mult'] * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] += 1
        user['win_streak'] += 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'hilo', win)
        result = f"📈 ХИЛО! Риск: {risk}\n💰 Выигрыш: {win} (x{risk_data['mult']})"
        add_game_history(user_id, '📈 Хило', bet, win, 'win')
    else:
        result = f"❌ Проигрыш! Риск: {risk}\n💰 Проигрыш: {bet}"
        user['total_losses'] += 1
        user['win_streak'] = 0
        user['total_lost'] += bet
        update_event_stats(user_id, 'hilo', 0)
        add_game_history(user_id, '📈 Хило', bet, 0, 'lose')
    user['max_win_streak'] = max(user['max_win_streak'], user['win_streak'])
    save_data()
    result += f"\n💰 Баланс: {user['balance']}"
    bot.send_message(message.chat.id, result)
    clear_game(user_id)

def start_pyramid_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    user['game'] = {
        'type': 'pyramid',
        'bet': bet,
        'chat_id': message.chat.id,
        'stage': 'playing_pyramid',
        'mine_position': random.randint(1, PYRAMID_CELLS)
    }
    save_data()
    set_game_timer(user_id)
    update_quest_progress(user_id, 'play', 1, 'pyramid')
    show_pyramid_field(message.chat.id, user['game'])

def show_pyramid_field(chat_id, game):
    markup = types.InlineKeyboardMarkup(row_width=PYRAMID_CELLS)
    buttons = []
    for i in range(1, PYRAMID_CELLS + 1):
        buttons.append(types.InlineKeyboardButton('🔺', callback_data=f"pyramid_cell_{i}"))
    markup.add(*buttons)
    bot.send_message(chat_id, 
                    f"🔺 Пирамида\n"
                    f"💰 Ставка: {game['bet']}\n"
                    f"Выбери ячейку (1-{PYRAMID_CELLS}):", 
                    reply_markup=markup)

def pyramid_cell_handler(user_id, call, cell):
    user = users.get(user_id)
    game = user['game']
    if cell == game['mine_position']:
        bot.edit_message_text(
            f"💥 Ты наступил на мину!\n"
            f"💰 Проигрыш: {game['bet']}\n"
            f"💰 Баланс: {user['balance']}",
            call.message.chat.id,
            call.message.message_id
        )
        user['total_losses'] += 1
        user['win_streak'] = 0
        user['total_lost'] += game['bet']
        update_event_stats(user_id, 'pyramid', 0)
        add_game_history(user_id, '🔺 Пирамида', game['bet'], 0, 'lose')
        clear_game(user_id)
        save_data()
        bot.answer_callback_query(call.id, "💥 Ты проиграл!")
    else:
        win = int(game['bet'] * PYRAMID_MULTIPLIER * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] += 1
        user['win_streak'] += 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'pyramid', win)
        add_game_history(user_id, '🔺 Пирамида', game['bet'], win, 'win')
        bot.edit_message_text(
            f"✅ Ты выбрал безопасную ячейку!\n"
            f"💰 Выигрыш: {win} (x{PYRAMID_MULTIPLIER})\n"
            f"💰 Баланс: {user['balance']}",
            call.message.chat.id,
            call.message.message_id
        )
        clear_game(user_id)
        save_data()
        bot.answer_callback_query(call.id, f"🎉 Выигрыш {win}!")

# ====================== СИСТЕМА КЕЙСОВ ======================
def show_cases_menu(chat_id, user_id):
    user = get_user(user_id)
    text = "📦 Магазин кейсов\n\n"
    text += "Открывай кейсы и получай случайные кредиксы!\n\n"
    for case_id, case in CASES.items():
        if case_id == 'case6' and not RELEASE_EVENT['active']:
            continue
        price_info = f"Цена: {case['price']}💰" if case['price'] > 0 else "Только за ивент-квесты"
        text += f"{case['icon']} {case['name']}\n"
        text += f"└ {price_info}\n"
        text += f"└ Выигрыш: {case['min_win']}-{case['max_win']}💰\n\n"
    text += f"💰 Твой баланс: {user['balance']} кредиксов\n"
    text += "Выбери кейс для открытия:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    for case_id, case in CASES.items():
        if case_id == 'case6' and not RELEASE_EVENT['active']:
            continue
        btn_text = f"{case['icon']} {case['name']}"
        if case['price'] > 0:
            btn_text += f" ({case['price']}💰)"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"case_open_{case_id}"))
    markup.add(types.InlineKeyboardButton("📊 Моя статистика", callback_data="case_stats"))
    markup.add(types.InlineKeyboardButton("🚪 Назад", callback_data="case_exit"))
    bot.send_message(chat_id, text, reply_markup=markup)

def open_case(user_id, case_id):
    user = get_user(user_id)
    if case_id not in CASES:
        return False, "❌ Кейс не найден."
    case = CASES[case_id]
    if case_id == 'case6':
        if not RELEASE_EVENT['active']:
            return False, "❌ Ивент не активен."
        # Проверка времени (раз в 24 часа)
        last_open = user.get('last_case6_open', 0)
        now = time.time()
        if now - last_open < 86400:
            remaining = 86400 - (now - last_open)
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            return False, f"❌ Ивентовый кейс можно открыть раз в 24 часа. Подожди ещё {hours} ч {minutes} мин."
        user['last_case6_open'] = now
    if case['price'] > 0 and user['balance'] < case['price']:
        return False, f"❌ Недостаточно средств. Нужно: {case['price']}💰."
    if case['price'] > 0:
        user['balance'] -= case['price']
    win = random.randint(case['min_win'], case['max_win'])
    user['balance'] += win
    if user_id not in user_cases:
        user_cases[user_id] = {}
    user_cases[user_id][case_id] = user_cases[user_id].get(case_id, 0) + 1
    add_game_history(user_id, f"{case['icon']} Кейс", case['price'], win, 'win')
    save_data()
    return True, f"🎉 Ты открыл {case['icon']} {case['name']} и получил {win}💰!"

def show_case_stats(chat_id, user_id):
    if user_id not in user_cases or not user_cases[user_id]:
        bot.send_message(chat_id, "📊 Ты ещё не открывал кейсы.")
        return
    text = "📊 Твоя статистика открытий кейсов\n\n"
    for case_id, count in user_cases[user_id].items():
        if case_id in CASES:
            case = CASES[case_id]
            text += f"{case['icon']} {case['name']}: {count} раз\n"
    bot.send_message(chat_id, text)

# ====================== СИСТЕМА ЗАДАНИЙ ======================
def reset_daily_quests(user_id):
    user_id = str(user_id)
    user_quests[user_id] = {}
    for quest_id, quest_data in DAILY_QUESTS.items():
        user_quests[user_id][quest_id] = {
            'progress': 0,
            'completed': False,
            'claimed': False
        }
    save_data()

def check_and_reset_quests(user_id):
    user_id = str(user_id)
    if user_id not in user_quests:
        reset_daily_quests(user_id)
        return
    last_reset = user_quests.get(user_id, {}).get('last_reset', 0)
    if time.time() - last_reset > 86400:
        reset_daily_quests(user_id)
        user_quests[user_id]['last_reset'] = time.time()
        save_data()

def update_quest_progress(user_id, quest_type, amount=1, game_type=None):
    user_id = str(user_id)
    check_and_reset_quests(user_id)
    if user_id not in user_quests:
        return []
    completed_quests = []
    user = get_user(user_id)
    for quest_id, quest_data in user_quests[user_id].items():
        if quest_id == 'last_reset':
            continue
        if not quest_data['completed']:
            quest_info = DAILY_QUESTS.get(quest_id)
            if not quest_info:
                continue
            if quest_info['type'] == quest_type:
                quest_data['progress'] += amount
            elif quest_type == 'play' and quest_info['type'] == game_type:
                quest_data['progress'] += amount
            elif quest_type == 'win' and quest_info['type'] == 'win':
                quest_data['progress'] += amount
            elif quest_type == 'earn' and quest_info['type'] == 'earn':
                quest_data['progress'] += amount * 1000
            if quest_data['progress'] >= quest_info['target']:
                quest_data['completed'] = True
                completed_quests.append(quest_id)
    save_data()
    return completed_quests

def claim_quest_reward(user_id, quest_id):
    user_id = str(user_id)
    if user_id not in user_quests:
        return False, "❌ Нет активных заданий"
    if quest_id not in user_quests[user_id]:
        return False, "❌ Задание не найдено"
    quest = user_quests[user_id][quest_id]
    if not quest['completed']:
        return False, "❌ Задание ещё не выполнено"
    if quest.get('claimed', False):
        return False, "❌ Награда уже получена"
    quest_info = DAILY_QUESTS.get(quest_id)
    if not quest_info:
        return False, "❌ Задание не найдено"
    reward = quest_info['reward']
    if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
        reward *= RELEASE_EVENT['bonus_quest_reward']
    user = get_user(user_id)
    user['balance'] += reward
    user['quests_completed'] = user.get('quests_completed', 0) + 1
    quest['claimed'] = True
    save_data()
    if user['quests_completed'] >= 50:
        if 'quest_master' not in user_achievements.get(user_id, {}):
            unlock_achievement(user_id, 'quest_master')
    return True, f"✅ Награда получена: +{int(reward)} кредиксов!"

def show_quests(chat_id, user_id):
    user_id = str(user_id)
    check_and_reset_quests(user_id)
    if user_id not in user_quests:
        reset_daily_quests(user_id)
    text = "📋 Ежедневные задания\n\n"
    text += "Выполняй задания и получай награды!\n"
    text += "Задания обновляются каждый день в 00:00 МСК\n\n"
    if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
        text += "🎉 ИВЕНТ! Награды за задания увеличены в 2 раза!\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for quest_id, quest_data in user_quests[user_id].items():
        if quest_id == 'last_reset':
            continue
        quest_info = DAILY_QUESTS.get(quest_id)
        if not quest_info:
            continue
        progress = quest_data['progress']
        target = quest_info['target']
        reward = quest_info['reward']
        if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
            reward *= RELEASE_EVENT['bonus_quest_reward']
        if quest_data['completed']:
            if quest_data.get('claimed', False):
                status = "✅ ВЫПОЛНЕНО (награда получена)"
                btn_text = f"{quest_info['icon']} {quest_info['name']} - награда получена"
                btn_data = f"quest_info_{quest_id}"
            else:
                status = "🎁 ГОТОВО К ПОЛУЧЕНИЮ!"
                btn_text = f"{quest_info['icon']} {quest_info['name']} - ЗАБРАТЬ {int(reward)}💰"
                btn_data = f"quest_claim_{quest_id}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=btn_data))
        else:
            status = f"⏳ В процессе: {progress}/{target}"
        text += f"{quest_info['icon']} {quest_info['name']}\n"
        text += f"└ {quest_info['desc']}\n"
        text += f"└ {status}\n"
        text += f"└ Награда: {int(reward)}💰\n\n"
    completed = sum(1 for q in user_quests[user_id].values() 
                   if isinstance(q, dict) and q.get('claimed', False))
    total = len([q for q in DAILY_QUESTS.keys()])
    text += f"📊 Выполнено заданий: {completed}/{total}"
    bot.send_message(chat_id, text, reply_markup=markup)

# ====================== СИСТЕМА ИВЕНТА ======================
def update_event_stats(user_id, game_type, win_amount=0):
    if not RELEASE_EVENT['active'] or time.time() >= RELEASE_EVENT['end_time']:
        return
    user_id = str(user_id)
    if user_id not in event_data['participants']:
        event_data['participants'][user_id] = {
            'points': 0,
            'games_played': 0,
            'wins': 0,
            'total_won': 0
        }
        if 'event_participant' not in user_achievements.get(user_id, {}):
            unlock_achievement(user_id, 'event_participant')
    event_data['participants'][user_id]['games_played'] += 1
    event_data['participants'][user_id]['points'] += 10
    if win_amount > 0:
        event_data['participants'][user_id]['wins'] += 1
        event_data['participants'][user_id]['total_won'] += win_amount
        event_data['participants'][user_id]['points'] += win_amount // 1000
    update_event_leaderboard()
    save_data()

def update_event_leaderboard():
    if not event_data['participants']:
        return
    sorted_participants = sorted(
        event_data['participants'].items(),
        key=lambda x: x[1]['points'],
        reverse=True
    )[:50]
    event_data['leaderboard'] = []
    for user_id, data in sorted_participants:
        try:
            user = bot.get_chat(int(user_id))
            name = user.first_name
            if user.username:
                name = f"@{user.username}"
        except:
            name = f"ID {user_id}"
        event_data['leaderboard'].append({
            'user_id': user_id,
            'name': name,
            'points': data['points'],
            'games': data['games_played'],
            'wins': data['wins']
        })
    event_data['last_update'] = time.time()
    save_data()

def show_event_menu(chat_id, user_id):
    if not RELEASE_EVENT['active']:
        bot.send_message(chat_id, "❌ В данный момент нет активных ивентов.")
        return
    if time.time() >= RELEASE_EVENT['end_time']:
        RELEASE_EVENT['active'] = False
        bot.send_message(chat_id, "❌ Ивент завершён.")
        return
    time_left = RELEASE_EVENT['end_time'] - time.time()
    days = int(time_left // 86400)
    hours = int((time_left % 86400) // 3600)
    text = f"🎉 {RELEASE_EVENT['name']} 🎉\n\n"
    text += f"⏱ До конца: {days}д {hours}ч\n\n"
    text += "Бонусы ивента:\n"
    text += f"• ✨ x{RELEASE_EVENT['multiplier']} ко всем выигрышам\n"
    text += f"• 📋 x{RELEASE_EVENT['bonus_quest_reward']} награда за задания\n"
    text += "• 🦫 Эксклюзивный ивентовый бобёр в маркете\n"
    text += "• 🎉 Ивентовый кейс в разделе Кейсы\n\n"
    if user_id in event_data['participants']:
        stats = event_data['participants'][user_id]
        text += "Твоя статистика:\n"
        text += f"• 🎮 Сыграно игр: {stats['games_played']}\n"
        text += f"• 🏆 Побед: {stats['wins']}\n"
        text += f"• 💰 Выиграно: {stats['total_won']} кредиксов\n"
        text += f"• ⭐️ Очков ивента: {stats['points']}\n\n"
    text += "Топ участников:\n"
    if event_data['leaderboard']:
        for i, player in enumerate(event_data['leaderboard'][:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {player['name']} — {player['points']} ⭐️\n"
    else:
        text += "Пока нет участников. Стань первым!\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 Моя статистика", callback_data="event_stats"),
        types.InlineKeyboardButton("🎁 Призы ивента", callback_data="event_prizes")
    )
    bot.send_message(chat_id, text, reply_markup=markup)

def get_event_multiplier():
    if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
        return RELEASE_EVENT['multiplier']
    return 1.0

# ====================== ДОСТИЖЕНИЯ ======================
def check_achievements(user_id):
    user = get_user(user_id)
    if user_id not in user_achievements:
        user_achievements[user_id] = {}
    if 'first_game' not in user_achievements[user_id] and user['games_played'] >= 1:
        unlock_achievement(user_id, 'first_game')
    if 'millionaire' not in user_achievements[user_id] and user['balance'] >= 1000000:
        unlock_achievement(user_id, 'millionaire')
    if 'beaver_collector' not in user_achievements[user_id]:
        beavers = user.get('beavers', {})
        if len(beavers) >= len(BEAVERS_DATA):
            unlock_achievement(user_id, 'beaver_collector')
    if 'high_roller' not in user_achievements[user_id] and user['total_bets'] >= 100000:
        unlock_achievement(user_id, 'high_roller')
    if 'lucky_winner' not in user_achievements[user_id] and user.get('max_win_streak', 0) >= 10:
        unlock_achievement(user_id, 'lucky_winner')
    if 'clan_leader' not in user_achievements[user_id]:
        clan_name = user.get('clan')
        if clan_name and clan_name in clans and clans[clan_name]['owner'] == user_id:
            if clans[clan_name]['level'] >= 5:
                unlock_achievement(user_id, 'clan_leader')
    if 'business_tycoon' not in user_achievements[user_id]:
        if user_id in businesses and len(businesses[user_id].get('businesses', [])) >= len(BUSINESSES_DATA):
            unlock_achievement(user_id, 'business_tycoon')
    if 'referral_master' not in user_achievements[user_id] and user['referrals'] >= 10:
        unlock_achievement(user_id, 'referral_master')

def unlock_achievement(user_id, achievement_id):
    if achievement_id not in achievements:
        return
    if user_id not in user_achievements:
        user_achievements[user_id] = {}
    if achievement_id in user_achievements[user_id]:
        return
    achievement = achievements[achievement_id]
    user_achievements[user_id][achievement_id] = time.time()
    user = get_user(user_id)
    user['balance'] += achievement['reward']
    save_data()
    try:
        bot.send_message(int(user_id), 
                        f"🏆 Достижение разблокировано!\n\n"
                        f"{achievement['name']}\n"
                        f"{achievement['desc']}\n"
                        f"💰 Награда: +{achievement['reward']} кредиксов")
    except:
        pass

# ====================== НОВЫЙ ЕЖЕДНЕВНЫЙ БОНУС ======================
def claim_new_daily_bonus(user_id):
    user = get_user(user_id)
    now = time.time()
    last = user.get('daily_last_claim', 0)
    streak = user.get('daily_streak', 0)
    if now - last < 86400:
        return False, f"❌ Следующий бонус через {format_time(86400 - (now - last))}"
    if now - last < 172800:
        streak += 1
    else:
        streak = 1
    bonus = random.randint(1000, 10000)
    user['balance'] += bonus
    user['daily_last_claim'] = now
    user['daily_streak'] = streak
    save_data()
    if streak >= 30:
        if 'daily_streak' not in user_achievements.get(user_id, {}):
            unlock_achievement(user_id, 'daily_streak')
    return True, f"✅ Ежедневный бонус получен!\n🔥 Streak: {streak} дней\n💰 +{bonus} кредиксов"

# ====================== ДЖЕКПОТ ======================
def add_to_jackpot(amount):
    jackpot['total'] += amount
    save_data()

def check_jackpot_win(user_id, bet):
    if random.random() < (bet / 1000000):
        win = jackpot['total']
        jackpot['total'] = 0
        jackpot['last_winner'] = user_id
        jackpot['last_win_time'] = time.time()
        jackpot['history'].append({
            'user_id': user_id,
            'amount': win,
            'time': time.time()
        })
        jackpot['history'] = jackpot['history'][-10:]
        if 'jackpot_winner' not in user_achievements.get(user_id, {}):
            unlock_achievement(user_id, 'jackpot_winner')
        save_data()
        return win
    return 0

# ====================== ДУЭЛИ ======================
def create_duel(user_id, target_username, bet, game):
    target_id = username_cache.get(target_username.lower())
    if not target_id:
        return False, "❌ Пользователь не найден"
    if target_id == user_id:
        return False, "❌ Нельзя вызвать на дуэль самого себя"
    user = get_user(user_id)
    if user['balance'] < bet:
        return False, f"❌ Недостаточно средств. Нужно {bet} кредиксов"
    target = get_user(target_id)
    if target['balance'] < bet:
        return False, "❌ У противника недостаточно средств"
    duel_id = str(int(time.time())) + str(random.randint(1000, 9999))
    duels[duel_id] = {
        'player1': user_id,
        'player2': target_id,
        'bet': bet,
        'game': game,
        'status': 'waiting',
        'created': time.time()
    }
    save_data()
    try:
        bot.send_message(int(target_id), 
                        f"⚔️ Дуэль!\n\n"
                        f"@{username_cache.get(user_id, 'Игрок')} вызывает тебя на дуэль!\n"
                        f"💰 Ставка: {bet} кредиксов\n"
                        f"🎮 Игра: {game}\n\n"
                        f"Принять: /duel_accept {duel_id}\n"
                        f"Отклонить: /duel_decline {duel_id}")
    except:
        pass
    return True, f"✅ Дуэль создана! Ожидаем ответа от @{target_username}"

def accept_duel(user_id, duel_id):
    if duel_id not in duels:
        return False, "❌ Дуэль не найдена"
    duel = duels[duel_id]
    if duel['player2'] != user_id:
        return False, "❌ Это не твоя дуэль"
    if duel['status'] != 'waiting':
        return False, "❌ Дуэль уже завершена"
    player1 = get_user(duel['player1'])
    player2 = get_user(user_id)
    if player1['balance'] < duel['bet'] or player2['balance'] < duel['bet']:
        return False, "❌ У одного из игроков недостаточно средств"
    player1['balance'] -= duel['bet']
    player2['balance'] -= duel['bet']
    duel['status'] = 'accepted'
    save_data()
    return True, f"✅ Дуэль принята! Начинаем игру {duel['game']} со ставкой {duel['bet']}"

def decline_duel(user_id, duel_id):
    if duel_id not in duels:
        return False, "❌ Дуэль не найдена"
    duel = duels[duel_id]
    if duel['player2'] != user_id:
        return False, "❌ Это не твоя дуэль"
    if duel['status'] != 'waiting':
        return False, "❌ Дуэль уже завершена"
    duel['status'] = 'declined'
    save_data()
    try:
        bot.send_message(int(duel['player1']), 
                        f"❌ Противник отклонил дуэль.\n"
                        f"💰 Ставка возвращена.")
    except:
        pass
    return True, "✅ Дуэль отклонена"

def play_duel(duel_id, winner_id):
    if duel_id not in duels:
        return
    duel = duels[duel_id]
    loser_id = duel['player1'] if duel['player2'] == winner_id else duel['player2']
    winner = get_user(winner_id)
    loser = get_user(loser_id)
    win_amount = duel['bet'] * 2
    winner['balance'] += win_amount
    duel['status'] = 'finished'
    duel['winner'] = winner_id
    save_data()
    try:
        bot.send_message(int(winner_id), 
                        f"⚔️ Дуэль!\n\n"
                        f"Поздравляем! Ты победил в дуэли!\n"
                        f"💰 Выигрыш: {win_amount} кредиксов")
    except:
        pass
    try:
        bot.send_message(int(loser_id), 
                        f"⚔️ Дуэль!\n\n"
                        f"К сожалению, ты проиграл дуэль.\n"
                        f"💰 Потеряно: {duel['bet']} кредиксов")
    except:
        pass

# ====================== КЛАНЫ ======================
def get_clan_bonus(user_id):
    user = get_user(user_id)
    clan_name = user.get('clan')
    if not clan_name or clan_name not in clans:
        return 1.0
    clan = clans[clan_name]
    level = clan.get('level', 1)
    return CLAN_LEVELS[level]['bonus']

def add_clan_exp(clan_name, exp):
    if clan_name in clans:
        clan = clans[clan_name]
        clan['exp'] += exp
        while clan['level'] < 5 and clan['exp'] >= CLAN_LEVELS[clan['level'] + 1]['exp_needed']:
            clan['level'] += 1

@bot.message_handler(commands=['clan', 'клан'])
def clan_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    args = message.text.split()
    user = get_user(user_id)
    if len(args) == 1:
        show_clan_menu(message.chat.id, user_id)
    elif args[1] == 'create' and len(args) >= 3:
        create_clan(message, user_id, ' '.join(args[2:]))
    elif args[1] == 'join' and len(args) == 3:
        join_clan(message, user_id, args[2])
    elif args[1] == 'leave':
        leave_clan(message, user_id)
    elif args[1] == 'info' and len(args) == 3:
        show_clan_info(message.chat.id, args[2])

def show_clan_menu(chat_id, user_id):
    user = get_user(user_id)
    clan_name = user.get('clan')
    text = "👥 Клановая система\n\n"
    if clan_name and clan_name in clans:
        clan = clans[clan_name]
        level_info = CLAN_LEVELS[clan['level']]
        text += f"Твой клан: {clan_name}\n"
        text += f"Уровень: {clan['level']} (макс. {level_info['max_members']} чел)\n"
        text += f"Опыт: {clan['exp']}/{level_info['exp_needed']}\n"
        text += f"Казна: {clan.get('balance', 0)}💰\n"
        text += f"Бонус клана: +{int((level_info['bonus']-1)*100)}% к выигрышам\n\n"
        text += "Участники:\n"
        for member_id in clan['members']:
            try:
                member = bot.get_chat(int(member_id))
                name = member.first_name
                if member.username:
                    name = f"@{member.username}"
                owner_tag = "👑" if member_id == clan['owner'] else ""
                text += f"{owner_tag} {name}\n"
            except:
                text += f"{owner_tag} ID {member_id}\n"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 Статистика", callback_data="clan_stats"),
            types.InlineKeyboardButton("🚪 Покинуть", callback_data="clan_leave")
        )
    else:
        text += "Ты не состоишь в клане.\n\n"
        text += "Команды:\n"
        text += "/clan create [название] - создать клан\n"
        text += "/clan join [название] - вступить в клан\n"
        text += "/clan info [название] - информация о клане\n\n"
        if clans:
            text += "🏆 Топ кланов:\n"
            sorted_clans = sorted(clans.items(), key=lambda x: x[1]['exp'], reverse=True)[:5]
            for i, (name, data) in enumerate(sorted_clans, 1):
                text += f"{i}. {name} (ур.{data['level']}) - {data['exp']} опыта\n"
        markup = None
    bot.send_message(chat_id, text, reply_markup=markup)

def create_clan(message, user_id, clan_name):
    user = get_user(user_id)
    if user.get('clan'):
        bot.send_message(message.chat.id, "❌ Ты уже состоишь в клане")
        return
    if clan_name in clans:
        bot.send_message(message.chat.id, "❌ Клан с таким названием уже существует")
        return
    if len(clan_name) > 20:
        bot.send_message(message.chat.id, "❌ Название клана не должно превышать 20 символов")
        return
    if user['balance'] < 50000:
        bot.send_message(message.chat.id, "❌ Для создания клана нужно 50,000 кредиксов")
        return
    user['balance'] -= 50000
    clans[clan_name] = {
        'owner': user_id,
        'members': [user_id],
        'level': 1,
        'exp': 0,
        'balance': 0,
        'wins': 0,
        'chat': []
    }
    user['clan'] = clan_name
    save_data()
    bot.send_message(message.chat.id, f"✅ Клан {clan_name} успешно создан!")

def join_clan(message, user_id, clan_name):
    user = get_user(user_id)
    if user.get('clan'):
        bot.send_message(message.chat.id, "❌ Ты уже состоишь в клане")
        return
    if clan_name not in clans:
        bot.send_message(message.chat.id, "❌ Клан не найден")
        return
    clan = clans[clan_name]
    max_members = CLAN_LEVELS[clan['level']]['max_members']
    if len(clan['members']) >= max_members:
        bot.send_message(message.chat.id, "❌ В клане нет мест")
        return
    clan['members'].append(user_id)
    user['clan'] = clan_name
    save_data()
    bot.send_message(message.chat.id, f"✅ Ты вступил в клан {clan_name}!")
    try:
        owner_id = int(clan['owner'])
        bot.send_message(owner_id, f"👥 Новый участник в клане: @{message.from_user.username}")
    except:
        pass

def leave_clan(message, user_id):
    user = get_user(user_id)
    clan_name = user.get('clan')
    if not clan_name or clan_name not in clans:
        bot.send_message(message.chat.id, "❌ Ты не состоишь в клане")
        return
    clan = clans[clan_name]
    if clan['owner'] == user_id:
        if len(clan['members']) > 1:
            bot.send_message(message.chat.id, "❌ Передай права владельца перед уходом")
            return
        else:
            del clans[clan_name]
            bot.send_message(message.chat.id, f"Клан {clan_name} распущен")
    else:
        clan['members'].remove(user_id)
        bot.send_message(message.chat.id, f"✅ Ты покинул клан {clan_name}")
    user['clan'] = None
    save_data()

def show_clan_info(chat_id, clan_name):
    if not clan_name or clan_name not in clans:
        bot.send_message(chat_id, "❌ Клан не найден")
        return
    clan = clans[clan_name]
    level_info = CLAN_LEVELS[clan['level']]
    text = f"🏰 Клан {clan_name}\n\n"
    text += f"Владелец: "
    try:
        owner = bot.get_chat(int(clan['owner']))
        text += f"@{owner.username}" if owner.username else f"ID {clan['owner']}"
    except:
        text += f"ID {clan['owner']}"
    text += f"\nУровень: {clan['level']}\n"
    text += f"Опыт: {clan['exp']}/{level_info['exp_needed']}\n"
    text += f"Участников: {len(clan['members'])}/{level_info['max_members']}\n"
    text += f"Казна: {clan.get('balance', 0)}💰\n"
    text += f"Бонус: +{int((level_info['bonus']-1)*100)}% к выигрышам\n\n"
    text += "Участники:\n"
    for member_id in clan['members']:
        try:
            member = bot.get_chat(int(member_id))
            name = f"@{member.username}" if member.username else member.first_name
            text += f"• {name}\n"
        except:
            text += f"• ID {member_id}\n"
    bot.send_message(chat_id, text)

# ====================== БИЗНЕСЫ ======================
def get_user_businesses(user_id):
    if user_id not in businesses:
        businesses[user_id] = {
            'businesses': [], 
            'last_collect': {},
            'levels': {}
        }
    return businesses[user_id]

@bot.message_handler(commands=['business', 'бизнесы'])
def business_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    args = message.text.split()
    if len(args) == 1:
        show_business_menu(message.chat.id, user_id)
    elif args[1] == 'buy' and len(args) == 3:
        buy_business(message, user_id, args[2])
    elif args[1] == 'upgrade' and len(args) == 3:
        upgrade_business(message, user_id, args[2])
    elif args[1] == 'collect':
        collect_business(message, user_id)

def show_business_menu(chat_id, user_id):
    user = get_user(user_id)
    user_biz = get_user_businesses(user_id)
    text = "💼 Система бизнесов\n\n"
    text += f"💰 Твой баланс: {user['balance']} кредиксов\n\n"
    if user_biz['businesses']:
        text += "Твои бизнесы:\n"
        now = time.time()
        for biz_id in user_biz['businesses']:
            if biz_id in BUSINESSES_DATA:
                biz_data = BUSINESSES_DATA[biz_id]
                last_collect = user_biz['last_collect'].get(biz_id, 0)
                time_left = max(0, last_collect + biz_data['cooldown'] - now)
                level = user_biz['levels'].get(biz_id, 1)
                income = biz_data['income'] * level
                if time_left > 0:
                    status = f"⏳ {format_time(time_left)}"
                else:
                    status = "✅ Готов к сбору"
                text += f"{biz_data['image']} {biz_data['name']} ур.{level}\n"
                text += f"└ Доход: {income}💰 | {status}\n"
        text += "\nКоманды:\n"
        text += "/business collect - собрать доход\n"
        text += "/business upgrade [id] - улучшить бизнес\n"
    else:
        text += "У тебя нет бизнесов. Купи свой первый бизнес:\n\n"
        for biz_id, data in BUSINESSES_DATA.items():
            text += f"{data['image']} {data['name']}\n"
            text += f"└ Цена: {data['price']}💰 | Доход: {data['income']}💰\n"
            text += f"└ Время: {format_time(data['cooldown'])}\n\n"
        text += "Купить: /business buy [id]\n"
        text += "ID: lime, kiosk, cafe, shop, restaurant, hotel"
    bot.send_message(chat_id, text)

def buy_business(message, user_id, biz_id):
    if biz_id not in BUSINESSES_DATA:
        bot.send_message(message.chat.id, "❌ Бизнес не найден")
        return
    user = get_user(user_id)
    user_biz = get_user_businesses(user_id)
    if biz_id in user_biz['businesses']:
        bot.send_message(message.chat.id, "❌ У тебя уже есть этот бизнес")
        return
    biz_data = BUSINESSES_DATA[biz_id]
    if user['balance'] < biz_data['price']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Нужно {biz_data['price']}💰")
        return
    user['balance'] -= biz_data['price']
    user_biz['businesses'].append(biz_id)
    user_biz['last_collect'][biz_id] = time.time()
    user_biz['levels'][biz_id] = 1
    save_data()
    bot.send_message(message.chat.id, 
                    f"✅ Ты купил {biz_data['image']} {biz_data['name']}!\n"
                    f"Доход можно собирать раз в {format_time(biz_data['cooldown'])}")

def upgrade_business(message, user_id, biz_id):
    user = get_user(user_id)
    user_biz = get_user_businesses(user_id)
    if biz_id not in user_biz['businesses']:
        bot.send_message(message.chat.id, "❌ У тебя нет этого бизнеса")
        return
    biz_data = BUSINESSES_DATA[biz_id]
    current_level = user_biz['levels'].get(biz_id, 1)
    if current_level >= biz_data['max_level']:
        bot.send_message(message.chat.id, "❌ Бизнес уже максимального уровня")
        return
    upgrade_cost = biz_data['upgrade_price'] * current_level
    if user['balance'] < upgrade_cost:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Нужно {upgrade_cost}💰")
        return
    user['balance'] -= upgrade_cost
    user_biz['levels'][biz_id] = current_level + 1
    save_data()
    bot.send_message(message.chat.id, 
                    f"✅ Бизнес улучшен до {current_level + 1} уровня!\n"
                    f"Новый доход: {biz_data['income'] * (current_level + 1)}💰")

def collect_business(message, user_id):
    user = get_user(user_id)
    user_biz = get_user_businesses(user_id)
    if not user_biz['businesses']:
        bot.send_message(message.chat.id, "❌ У тебя нет бизнесов")
        return
    now = time.time()
    total_income = 0
    collected = []
    clan_bonus = get_clan_bonus(user_id)
    global_mult = get_global_multiplier(user_id)
    for biz_id in user_biz['businesses']:
        if biz_id in BUSINESSES_DATA:
            biz_data = BUSINESSES_DATA[biz_id]
            last_collect = user_biz['last_collect'].get(biz_id, 0)
            if now - last_collect >= biz_data['cooldown']:
                level = user_biz['levels'].get(biz_id, 1)
                income = biz_data['income'] * level
                income = int(income * clan_bonus * global_mult)
                total_income += income
                user_biz['last_collect'][biz_id] = now
                collected.append(f"{biz_data['image']} +{income}💰")
    if total_income > 0:
        user['balance'] += total_income
        save_data()
        clan_name = user.get('clan')
        if clan_name and clan_name in clans:
            add_clan_exp(clan_name, total_income // 100)
        bonus_text = f" (+{int((clan_bonus-1)*100)}% бонус клана, +{int((global_mult-1)*100)}% бобры)" if clan_bonus > 1 or global_mult > 1 else ""
        bot.send_message(message.chat.id, 
                        f"✅ Собрано:\n" + "\n".join(collected) + 
                        f"\n\n💰 Всего: +{total_income} кредиксов{bonus_text}")
    else:
        bot.send_message(message.chat.id, "❌ Нет готовых к сбору бизнесов")

# ====================== ДЖЕКПОТ ======================
def start_jackpot_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    jackpot_contribution = bet // 100
    add_to_jackpot(jackpot_contribution)
    jackpot_win = check_jackpot_win(user_id, bet)
    if jackpot_win > 0:
        user['balance'] += jackpot_win
        result_text = f"🎰 ДЖЕКПОТ! 🎰\n\n"
        result_text += f"Ты выиграл главный приз!\n"
        result_text += f"💰 {jackpot_win} кредиксов!\n\n"
    else:
        result_text = ""
    update_quest_progress(user_id, 'play', 1, 'jackpot')
    if random.random() < 0.4:
        win = int(bet * 2 * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'jackpot', win)
        result_text += f"🎉 Ты выиграл {win} кредиксов (x2)!"
        add_game_history(user_id, '🎰 Джекпот', bet, win, 'win')
    else:
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        result_text += f"❌ Ты проиграл {bet} кредиксов."
        add_game_history(user_id, '🎰 Джекпот', bet, 0, 'lose')
    result_text += f"\n\n💰 Текущий джекпот: {jackpot['total']} кредиксов\n"
    result_text += f"💰 Новый баланс: {user['balance']}"
    bot.send_message(message.chat.id, result_text)
    save_data()
    clear_game(user_id)

# ====================== МИНЫ ======================
def start_mines_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    user['game'] = {
        'type': 'mines',
        'bet': bet,
        'chat_id': message.chat.id,
        'stage': 'choosing_mines_count'
    }
    save_data()
    set_game_timer(user_id)
    update_quest_progress(user_id, 'play', 1, 'mines')
    markup = types.InlineKeyboardMarkup(row_width=5)
    markup.add(
        types.InlineKeyboardButton("1 💣", callback_data="mines_count_1"),
        types.InlineKeyboardButton("2 💣", callback_data="mines_count_2"),
        types.InlineKeyboardButton("3 💣", callback_data="mines_count_3"),
        types.InlineKeyboardButton("4 💣", callback_data="mines_count_4"),
        types.InlineKeyboardButton("5 💣", callback_data="mines_count_5")
    )
    bot.send_message(message.chat.id, 
                    f"💰 Ставка: {bet} кредиксов\n"
                    f"💣 Выбери количество мин (1-5):", 
                    reply_markup=markup)

def show_mines_field(chat_id, game):
    opened = game.get('opened', [])
    mines = game.get('mines', [])
    mines_count = len(mines)
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 26):
        if i in opened:
            if i in mines:
                emoji = '💣'
            else:
                emoji = '✅'
        else:
            emoji = '📦'
        buttons.append(types.InlineKeyboardButton(emoji, callback_data=f"mines_cell_{i}"))
    for i in range(0, 25, 5):
        markup.add(*buttons[i:i+5])
    opened_count = len(opened)
    safe_count = 25 - mines_count
    if opened_count > 0:
        if opened_count in MINES_MULTIPLIERS[mines_count]:
            current_mult = MINES_MULTIPLIERS[mines_count][opened_count]
        else:
            max_opened = max(MINES_MULTIPLIERS[mines_count].keys())
            current_mult = MINES_MULTIPLIERS[mines_count][max_opened]
    else:
        current_mult = 1.0
    current_win = int(game['bet'] * current_mult)
    markup.add(types.InlineKeyboardButton(f"💰 Забрать {current_win}💰", callback_data="mines_take"))
    bot.send_message(chat_id, 
                    f"💣 Мины!\n"
                    f"Мин: {mines_count}\n"
                    f"Открыто: {opened_count}/{safe_count}\n"
                    f"Текущий множитель: x{current_mult:.2f}\n"
                    f"Потенциальный выигрыш: {current_win}💰",
                    reply_markup=markup)

# ====================== БАШНЯ ======================
def start_tower_game(message, bet, mines=1):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    user['game'] = {
        'type': 'tower',
        'bet': bet,
        'chat_id': message.chat.id,
        'stage': 'playing_tower'
    }
    cells = list(range(1, 6))
    random.shuffle(cells)
    mine_positions = set(cells[:mines])
    safe_positions = set(cells[mines:])
    user['game']['mines'] = list(mine_positions)
    user['game']['safe'] = list(safe_positions)
    user['game']['opened'] = []
    user['game']['steps'] = 0
    save_data()
    set_game_timer(user_id)
    update_quest_progress(user_id, 'play', 1, 'tower')
    show_tower_field(message.chat.id, user['game'])

def show_tower_field(chat_id, game):
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for cell in range(1, 6):
        if cell not in game['opened']:
            buttons.append(types.InlineKeyboardButton(f"📦 {cell}", callback_data=f"tower_cell_{cell}"))
    if buttons:
        markup.add(*buttons)
    bot.send_message(chat_id, "📦 Выбери ячейку, чтобы открыть (всего 5 ячеек):", reply_markup=markup)

def tower_cell_handler(user_id, call, cell):
    user = users.get(user_id)
    game = user['game']
    if cell in game['opened']:
        bot.answer_callback_query(call.id, "📦 Ячейка уже открыта")
        return
    if cell in game['mines']:
        bot.edit_message_text(
            f"💥 Ты открыл мину! Ты проиграл {game['bet']} кредиксов.\n💰 Баланс: {user['balance']}",
            call.message.chat.id,
            call.message.message_id
        )
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + game['bet']
        update_event_stats(user_id, 'tower', 0)
        add_game_history(user_id, '🏰 Башня', game['bet'], 0, 'lose')
        clear_game(user_id)
        save_data()
        bot.answer_callback_query(call.id, "💥 Ты проиграл!")
    else:
        game['opened'].append(cell)
        game['steps'] += 1
        current_mult = TOWER_MULTIPLIERS[game['steps']]
        current_win = int(game['bet'] * current_mult * get_global_multiplier(user_id) * get_event_multiplier())
        if len(game['opened']) == len(game['safe']):
            user['balance'] += current_win
            user['total_wins'] = user.get('total_wins', 0) + 1
            user['win_streak'] = user.get('win_streak', 0) + 1
            user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
            update_quest_progress(user_id, 'win', 1)
            update_quest_progress(user_id, 'earn', current_win // 1000)
            update_event_stats(user_id, 'tower', current_win)
            add_game_history(user_id, '🏰 Башня', game['bet'], current_win, 'win')
            save_data()
            bot.edit_message_text(
                f"🎉 Ты открыл все безопасные ячейки!\n💰 Твой выигрыш: {current_win} кредиксов (x{current_mult})\n💰 Новый баланс: {user['balance']}",
                call.message.chat.id,
                call.message.message_id
            )
            clear_game(user_id)
            bot.answer_callback_query(call.id, "🎉 Ты выиграл!")
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ Забрать", callback_data="tower_take"),
                types.InlineKeyboardButton("🔄 Продолжить", callback_data="tower_continue")
            )
            bot.edit_message_text(
                f"✅ Ячейка {cell} безопасна!\n📦 Ты открыл {game['steps']} из 5 ячеек.\n"
                f"📈 Текущий множитель: x{current_mult}\n"
                f"💰 Если остановишься, получишь {current_win} кредиксов.",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
            save_data()
            bot.answer_callback_query(call.id)

def tower_take_handler(user_id, call):
    user = users.get(user_id)
    game = user['game']
    steps = game['steps']
    if steps == 0:
        bot.answer_callback_query(call.id, "📦 Ты ещё не открыл ни одной ячейки.")
        return
    current_mult = TOWER_MULTIPLIERS[steps]
    win = int(game['bet'] * current_mult * get_global_multiplier(user_id) * get_event_multiplier())
    user['balance'] += win
    user['total_wins'] = user.get('total_wins', 0) + 1
    user['win_streak'] = user.get('win_streak', 0) + 1
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    update_quest_progress(user_id, 'win', 1)
    update_quest_progress(user_id, 'earn', win // 1000)
    update_event_stats(user_id, 'tower', win)
    add_game_history(user_id, '🏰 Башня', game['bet'], win, 'win')
    save_data()
    bot.edit_message_text(
        f"✅ Ты забрал выигрыш: {win} кредиксов (x{current_mult})\n💰 Новый баланс: {user['balance']}",
        call.message.chat.id,
        call.message.message_id
    )
    clear_game(user_id)
    bot.answer_callback_query(call.id, f"🎉 Выигрыш {win}!")

# ====================== ФИШКИ ======================
def start_color_game(message, bet, color):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'color')
    result = random.choice(['black', 'white'])
    if color == result:
        win = int(bet * 2 * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'color', win)
        result_text = f"🎉 Выпало {'⚫️ чёрное' if result == 'black' else '⚪️ белое'}! Ты угадал!\n💰 Ты выиграл {win} кредиксов!"
        add_game_history(user_id, '⚫️⚪️ Фишки', bet, win, 'win')
    else:
        result_text = f"❌ Выпало {'⚫️ чёрное' if result == 'black' else '⚪️ белое'}. Ты проиграл {bet} кредиксов."
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'color', 0)
        add_game_history(user_id, '⚫️⚪️ Фишки', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    bot.send_message(message.chat.id, f"{result_text}\n💰 Новый баланс: {user['balance']}")
    clear_game(user_id)
    save_data()

# ====================== X2/X3/X5 ======================
def start_random_x_game(message, bet, mult):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'random_x')
    chances = {2:50, 3:30, 5:20}
    chance = chances.get(mult, 50)
    if random.randint(1, 100) <= chance:
        win = int(bet * mult * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'random_x', win)
        result_text = f"🎉 Удача! x{mult} сработало!\n💰 Ты выиграл {win} кредиксов!"
        add_game_history(user_id, f'🎲 x{mult}', bet, win, 'win')
    else:
        result_text = f"❌ Не повезло. Ты проиграл {bet} кредиксов."
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'random_x', 0)
        add_game_history(user_id, f'🎲 x{mult}', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    bot.send_message(message.chat.id, f"{result_text}\n💰 Новый баланс: {user['balance']}")
    clear_game(user_id)
    save_data()

# ====================== РУССКАЯ РУЛЕТКА ======================
def start_russian_roulette_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'russian_roulette')
    survival_chance = 5/6
    if random.random() < survival_chance:
        win = int(bet * 1.75 * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'russian_roulette', win)
        result_text = f"😌 Щелчок... Ты выжил!\n💰 Ты выиграл {win} кредиксов (x1.75)!"
        add_game_history(user_id, '🔫 Русская рулетка', bet, win, 'win')
    else:
        result_text = f"💥 Бах! Тебе не повезло...\nТы проиграл {bet} кредиксов."
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'russian_roulette', 0)
        add_game_history(user_id, '🔫 Русская рулетка', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    bot.send_message(message.chat.id, f"{result_text}\n💰 Новый баланс: {user['balance']}")
    clear_game(user_id)
    save_data()

# ====================== ОЧКО (21) ======================
def get_card():
    values = list(range(2, 10)) + [10]*4 + [11]
    return random.choice(values)

def calc_hand(hand):
    return sum(hand)

def hand_to_str(hand):
    cards = []
    for card in hand:
        if card == 11:
            cards.append('Т')
        elif card == 10:
            cards.append('10')
        else:
            cards.append(str(card))
    return ' + '.join(cards)

def start_blackjack_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    user['game'] = {
        'type': 'blackjack',
        'bet': bet,
        'chat_id': message.chat.id,
        'stage': 'playing_21'
    }
    update_quest_progress(user_id, 'play', 1, 'blackjack')
    player_hand = [get_card(), get_card()]
    dealer_hand = [get_card(), get_card()]
    user['game']['player_hand'] = player_hand
    user['game']['dealer_hand'] = dealer_hand
    save_data()
    set_game_timer(user_id)
    player_sum = calc_hand(player_hand)
    dealer_visible = dealer_hand[0]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎴 Ещё", callback_data="21_hit"),
        types.InlineKeyboardButton("🛑 Хватит", callback_data="21_stand")
    )
    msg = (f"🃏 Очко (21)\n\n"
           f"💰 Ставка: {bet} кредиксов\n"
           f"👤 Твои карты: {hand_to_str(player_hand)} = {player_sum}\n"
           f"🤵 Карта дилера: {dealer_visible}\n\n"
           f"Выбери действие:")
    bot.send_message(message.chat.id, msg, reply_markup=markup)

# ====================== КРАШ ======================
def start_crash_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    update_quest_progress(user_id, 'play', 1, 'crash')
    user['balance'] -= bet
    crash_point = generate_crash_point()
    user['game'] = {
        'type': 'crash',
        'bet': bet,
        'chat_id': message.chat.id,
        'stage': 'playing_crash',
        'crash_point': crash_point,
        'current_mult': 1.0,
        'active': True,
        'message_id': None
    }
    save_data()
    set_game_timer(user_id)
    if user_id not in crash_locks:
        crash_locks[user_id] = Lock()
    bonuses = get_beaver_bonuses(user_id)
    crash_bonus = bonuses.get('crash_mult_bonus', 0)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Забрать", callback_data="crash_take"))
    msg = bot.send_message(
        message.chat.id,
        f"🚀 КРАШ ИГРА\n\n"
        f"💰 Ставка: {bet} кредиксов\n"
        f"📈 Текущий множитель: 1.00x\n"
        f"✨ Бонус бобров: +{crash_bonus}% к выигрышу\n\n"
        f"Забери выигрыш до взрыва!",
        reply_markup=markup
    )
    user['game']['message_id'] = msg.message_id
    save_data()
    timer = Timer(0.5, update_crash, [user_id])
    timer.daemon = True
    crash_update_timers[user_id] = timer
    timer.start()

def generate_crash_point():
    r = random.random()
    if r < 0.05:
        return 1.0 + random.random() * 0.3
    elif r < 0.2:
        return 1.3 + random.random() * 0.7
    elif r < 0.5:
        return 2.0 + random.random() * 3.0
    elif r < 0.8:
        return 5.0 + random.random() * 5.0
    else:
        return 10.0 + random.random() * 90.0

def update_crash(user_id):
    user_id = str(user_id)
    if user_id in crash_locks:
        with crash_locks[user_id]:
            _update_crash_locked(user_id)
    else:
        _update_crash_locked(user_id)

def _update_crash_locked(user_id):
    user = users.get(user_id)
    if not user or user.get('game') is None or user['game'].get('type') != 'crash':
        if user_id in crash_update_timers:
            crash_update_timers[user_id].cancel()
            del crash_update_timers[user_id]
        return
    game = user['game']
    if not game.get('active', False):
        return
    chat_id = game.get('chat_id', int(user_id))
    current = game['current_mult']
    crash_point = game['crash_point']
    message_id = game.get('message_id')
    bet = game['bet']
    new_mult = current * 1.025
    new_mult = round(new_mult, 2)
    if new_mult >= crash_point:
        game['active'] = False
        game['stage'] = 'crashed'
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'crash', 0)
        add_game_history(user_id, '🚀 Краш', bet, 0, 'lose')
        try:
            bot.edit_message_text(
                f"💥 РАКЕТА ВЗОРВАЛАСЬ! 💥\n\n"
                f"💰 Ставка: {bet} кредиксов\n"
                f"💥 Множитель краша: {crash_point:.2f}x\n"
                f"📈 Ты не успел забрать...\n\n"
                f"❌ Ты проиграл {bet} кредиксов.\n"
                f"💰 Новый баланс: {user['balance']}",
                chat_id,
                message_id
            )
        except:
            pass
        if user_id in crash_update_timers:
            crash_update_timers[user_id].cancel()
            del crash_update_timers[user_id]
        if user_id in game_timers:
            game_timers[user_id].cancel()
            del game_timers[user_id]
        user['game'] = None
        save_data()
        return
    game['current_mult'] = new_mult
    save_data()
    bonuses = get_beaver_bonuses(user_id)
    crash_bonus = bonuses.get('crash_mult_bonus', 0)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Забрать", callback_data="crash_take"))
    try:
        potential_win = int(bet * new_mult * (1 + crash_bonus/100) * get_global_multiplier(user_id) * get_event_multiplier())
        bot.edit_message_text(
            f"🚀 КРАШ ИГРА\n\n"
            f"💰 Ставка: {bet} кредиксов\n"
            f"📈 Текущий множитель: {new_mult:.2f}x\n"
            f"✨ Бонус бобров: +{crash_bonus}% к выигрышу\n"
            f"💎 Потенциальный выигрыш: {potential_win}💰\n\n"
            f"Забери выигрыш до взрыва!",
            chat_id,
            message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка обновления краша: {e}")
        if user_id in crash_update_timers:
            crash_update_timers[user_id].cancel()
            del crash_update_timers[user_id]
        if user_id in game_timers:
            game_timers[user_id].cancel()
            del game_timers[user_id]
        user['balance'] += bet
        user['game'] = None
        save_data()
        return
    set_game_timer(user_id)
    delay = 0.4 if new_mult < 3.0 else (0.5 if new_mult < 10.0 else 0.6)
    timer = Timer(delay, update_crash, [user_id])
    timer.daemon = True
    crash_update_timers[user_id] = timer
    timer.start()

def crash_take_win(user_id, call):
    user = users.get(user_id)
    if not user or user.get('game') is None or user['game'].get('type') != 'crash':
        bot.answer_callback_query(call.id, "❌ Игра не найдена")
        return False
    game = user['game']
    if user_id in crash_locks:
        with crash_locks[user_id]:
            return _crash_take_win_locked(user_id, call)
    else:
        return _crash_take_win_locked(user_id, call)

def _crash_take_win_locked(user_id, call):
    user = users.get(user_id)
    game = user['game']
    if not game.get('active', False):
        bot.answer_callback_query(call.id, "❌ Игра уже завершена")
        return False
    bet = game['bet']
    current_mult = game['current_mult']
    crash_point = game['crash_point']
    if current_mult >= crash_point:
        bot.answer_callback_query(call.id, "💥 Ракета уже взорвалась!")
        return False
    bonuses = get_beaver_bonuses(user_id)
    crash_bonus = 1 + bonuses.get('crash_mult_bonus', 0) / 100
    global_mult = get_global_multiplier(user_id)
    event_mult = get_event_multiplier()
    win = int(bet * current_mult * crash_bonus * global_mult * event_mult)
    user['balance'] += win
    user['total_wins'] = user.get('total_wins', 0) + 1
    user['win_streak'] = user.get('win_streak', 0) + 1
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    update_quest_progress(user_id, 'win', 1)
    update_quest_progress(user_id, 'earn', win // 1000)
    update_event_stats(user_id, 'crash', win)
    add_game_history(user_id, '🚀 Краш', bet, win, 'win')
    game['active'] = False
    if user_id in crash_update_timers:
        crash_update_timers[user_id].cancel()
        del crash_update_timers[user_id]
    if user_id in game_timers:
        game_timers[user_id].cancel()
        del game_timers[user_id]
    try:
        win_text = (
            f"🎉 ТЫ ЗАБРАЛ ВЫИГРЫШ! 🎉\n\n"
            f"💰 Ставка: {bet} кредиксов\n"
            f"📈 Множитель: {current_mult:.2f}x\n"
            f"💥 Ракета взорвалась бы на: {crash_point:.2f}x\n"
            f"✨ Бонус бобров: +{int((crash_bonus-1)*100)}%\n"
            f"🎉 Бонус ивента: x{event_mult}\n"
            f"🦫 Общий бонус бобров: x{global_mult:.2f}\n\n"
            f"✅ Ты выиграл: {win} кредиксов!\n"
            f"💰 Новый баланс: {user['balance']}"
        )
        bot.edit_message_text(
            win_text,
            call.message.chat.id,
            call.message.message_id
        )
    except:
        bot.send_message(
            call.message.chat.id,
            f"🎉 Ты выиграл {win} кредиксов в Краше! Новый баланс: {user['balance']}"
        )
    user['game'] = None
    save_data()
    bot.answer_callback_query(call.id, f"🎉 Ты выиграл {win} кредиксов!")
    return True

# ====================== СЛОТЫ ======================
def start_slots_game(message, bet):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'slots')
    slots_message = bot.send_message(message.chat.id, "🎰 Крутим слоты...")
    time.sleep(1)
    result_text, win = slots_spin(user_id, bet)
    bot.edit_message_text(result_text, message.chat.id, slots_message.message_id)
    if win > bet:
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'slots', win)
        add_game_history(user_id, '🎰 Слоты', bet, win, 'win')
    else:
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        if win < bet:
            user['total_lost'] = user.get('total_lost', 0) + (bet - win)
        update_event_stats(user_id, 'slots', 0)
        add_game_history(user_id, '🎰 Слоты', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    save_data()
    clear_game(user_id)

def slots_spin(user_id, bet):
    user = get_user(user_id)
    bonuses = get_beaver_bonuses(user_id)
    slots_bonus = bonuses.get('slots_bonus', 0) / 100
    symbols = [random.choice(SLOTS_SYMBOLS) for _ in range(3)]
    combo = tuple(symbols)
    event_mult = get_event_multiplier()
    global_mult = get_global_multiplier(user_id)
    if combo in SLOTS_PAYOUTS:
        mult = SLOTS_PAYOUTS[combo]
        win = int(bet * mult * (1 + slots_bonus) * event_mult * global_mult)
        user['balance'] += win
        result_text = f"🎰 {symbols[0]} | {symbols[1]} | {symbols[2]} 🎰\n\n"
        result_text += f"🎉 Выигрышная комбинация! x{mult}\n"
        result_text += f"✨ Бонус бобров: +{int(slots_bonus*100)}%\n"
        result_text += f"🎉 Бонус ивента: x{event_mult}\n"
        result_text += f"🦫 Общий бонус бобров: x{global_mult:.2f}\n"
        result_text += f"💰 Выигрыш: {win} кредиксов."
    elif symbols[0] == symbols[1] or symbols[1] == symbols[2] or symbols[0] == symbols[2]:
        win = bet
        user['balance'] += win
        result_text = f"🎰 {symbols[0]} | {symbols[1]} | {symbols[2]} 🎰\n\n"
        result_text += f"🤝 Два одинаковых! Ставка возвращена.\n💰 Возврат: {bet} кредиксов."
    else:
        win = 0
        result_text = f"🎰 {symbols[0]} | {symbols[1]} | {symbols[2]} 🎰\n\n"
        result_text += f"❌ Неудачная комбинация. Ты проиграл {bet} кредиксов."
    save_data()
    return result_text, win

# ====================== КОСТИ ======================
def start_dice_game(message, bet, dice_type, dice_choice):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'dice')
    total = random.randint(2, 12)
    win = 0
    if dice_type == 'number':
        if total == dice_choice:
            win = bet * 6
            result_text = f"🎲 Выпало {total}! Ты угадал число! x6"
        else:
            result_text = f"🎲 Выпало {total}. Ты не угадал."
    elif dice_type == 'even_odd':
        if dice_choice == 'even' and total % 2 == 0:
            win = bet * 2
            result_text = f"🎲 Выпало {total} (чётное)! Ты выиграл! x2"
        elif dice_choice == 'odd' and total % 2 == 1:
            win = bet * 2
            result_text = f"🎲 Выпало {total} (нечётное)! Ты выиграл! x2"
        else:
            result_text = f"🎲 Выпало {total}. Ты проиграл."
    elif dice_type == 'range':
        if dice_choice == 'over7' and total > 7:
            win = bet * 2
            result_text = f"🎲 Выпало {total} (больше 7)! Ты выиграл! x2"
        elif dice_choice == 'under7' and total < 7:
            win = bet * 2
            result_text = f"🎲 Выпало {total} (меньше 7)! Ты выиграл! x2"
        else:
            result_text = f"🎲 Выпало {total}. Ты проиграл."
    if win > 0:
        win = int(win * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'dice', win)
        add_game_history(user_id, '🎲 Кости', bet, win, 'win')
    else:
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'dice', 0)
        add_game_history(user_id, '🎲 Кости', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    bot.send_message(message.chat.id, f"{result_text}\n💰 Новый баланс: {user['balance']}")
    clear_game(user_id)
    save_data()

# ====================== РУЛЕТКА ======================
def get_color_emoji(color):
    if color == 'red':
        return '🔴'
    elif color == 'black':
        return '⚫️'
    else:
        return '🟢'

def get_roulette_bet_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔢 Число (x36)", callback_data="roulette_type_straight"),
        types.InlineKeyboardButton("🔴 Красное (x2)", callback_data="roulette_type_red"),
        types.InlineKeyboardButton("⚫️ Чёрное (x2)", callback_data="roulette_type_black"),
        types.InlineKeyboardButton("🟢 0 (x36)", callback_data="roulette_type_zero"),
        types.InlineKeyboardButton("🔲 Чётное (x2)", callback_data="roulette_type_even"),
        types.InlineKeyboardButton("🔳 Нечётное (x2)", callback_data="roulette_type_odd"),
        types.InlineKeyboardButton("1-18 (x2)", callback_data="roulette_type_1-18"),
        types.InlineKeyboardButton("19-36 (x2)", callback_data="roulette_type_19-36"),
        types.InlineKeyboardButton("1-12 (x3)", callback_data="roulette_type_1st"),
        types.InlineKeyboardButton("13-24 (x3)", callback_data="roulette_type_2nd"),
        types.InlineKeyboardButton("25-36 (x3)", callback_data="roulette_type_3rd")
    )
    return markup

def roulette_spin():
    number = random.choice(ROULETTE_NUMBERS)
    color = 'green' if number == 0 else ('red' if number in RED_NUMBERS else 'black')
    return number, color

def roulette_result(bet, bet_type, bet_value, number, color):
    win = 0
    multiplier = 0
    if bet_type == 'straight':
        if number == bet_value:
            multiplier = ROULETTE_MULTIPLIERS['straight']
            win = bet * multiplier
    elif bet_type == 'color':
        if color == bet_value:
            multiplier = ROULETTE_MULTIPLIERS['color']
            win = bet * multiplier
    elif bet_type == 'even_odd':
        if number != 0:
            if bet_value == 'even' and number % 2 == 0:
                multiplier = ROULETTE_MULTIPLIERS['even']
                win = bet * multiplier
            elif bet_value == 'odd' and number % 2 == 1:
                multiplier = ROULETTE_MULTIPLIERS['odd']
                win = bet * multiplier
    elif bet_type == 'range':
        if number != 0:
            if bet_value == '1-18' and 1 <= number <= 18:
                multiplier = ROULETTE_MULTIPLIERS['1-18']
                win = bet * multiplier
            elif bet_value == '19-36' and 19 <= number <= 36:
                multiplier = ROULETTE_MULTIPLIERS['19-36']
                win = bet * multiplier
    elif bet_type == 'dozen':
        if number != 0:
            if bet_value == '1st' and 1 <= number <= 12:
                multiplier = ROULETTE_MULTIPLIERS['dozen']
                win = bet * multiplier
            elif bet_value == '2nd' and 13 <= number <= 24:
                multiplier = ROULETTE_MULTIPLIERS['dozen']
                win = bet * multiplier
            elif bet_value == '3rd' and 25 <= number <= 36:
                multiplier = ROULETTE_MULTIPLIERS['dozen']
                win = bet * multiplier
    return win, multiplier

def start_roulette_game(message, bet, bet_type, bet_value=None):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if bet > user['balance']:
        bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
        return
    if bet > MAX_BET:
        bot.send_message(message.chat.id, f"❌ Максимальная ставка: {MAX_BET}")
        return
    user['balance'] -= bet
    update_quest_progress(user_id, 'play', 1, 'roulette')
    number, color = roulette_spin()
    win, mult = roulette_result(bet, bet_type, bet_value, number, color)
    if win > 0:
        win = int(win * get_global_multiplier(user_id) * get_event_multiplier())
        user['balance'] += win
        user['total_wins'] = user.get('total_wins', 0) + 1
        user['win_streak'] = user.get('win_streak', 0) + 1
        update_quest_progress(user_id, 'win', 1)
        update_quest_progress(user_id, 'earn', win // 1000)
        update_event_stats(user_id, 'roulette', win)
        result_text = f"🎉 Выпало {number} {get_color_emoji(color)}! Ты выиграл {win} кредиксов"
        if mult > 0:
            result_text += f" (x{mult})"
        add_game_history(user_id, '🎰 Рулетка', bet, win, 'win')
    else:
        result_text = f"❌ Выпало {number} {get_color_emoji(color)}. Ты проиграл {bet} кредиксов."
        user['total_losses'] = user.get('total_losses', 0) + 1
        user['win_streak'] = 0
        user['total_lost'] = user.get('total_lost', 0) + bet
        update_event_stats(user_id, 'roulette', 0)
        add_game_history(user_id, '🎰 Рулетка', bet, 0, 'lose')
    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
    save_data()
    result_text += f"\n💰 Новый баланс: {user['balance']}"
    bot.send_message(message.chat.id, result_text)
    clear_game(user_id)

# ====================== БАНК ======================
def apply_bank_interest(user_id):
    user = get_user(user_id)
    bank = user.get('bank', {'balance': 0, 'last_interest': time.time(), 'history': []})
    now = time.time()
    if now - bank['last_interest'] >= BANK_INTEREST_INTERVAL and bank['balance'] > 0:
        bonuses = get_beaver_bonuses(user_id)
        bank_bonus = 1 + bonuses.get('bank_interest_bonus', 0) / 100
        interest = int(bank['balance'] * BANK_INTEREST_RATE * bank_bonus)
        if interest > 0:
            bank['balance'] += interest
            timestamp = time.strftime("%d.%m %H:%M")
            bank['history'].insert(0, f"💹 Проценты +{interest} (с бонусом {int((bank_bonus-1)*100)}%) — {timestamp}")
            bank['history'] = bank['history'][:10]
        bank['last_interest'] = now
        user['bank'] = bank
        save_data()

def show_bank_menu(chat_id, user_id):
    user = get_user(user_id)
    bank = user.get('bank', {'balance': 0})
    bonuses = get_beaver_bonuses(user_id)
    bank_bonus = bonuses.get('bank_interest_bonus', 0)
    text = (f"🏦 Банк\n\n"
            f"💰 Основной баланс: {user['balance']} кредиксов\n"
            f"🏦 На депозите: {bank['balance']} кредиксов\n"
            f"📈 Процентная ставка: {BANK_INTEREST_RATE*100}% в 24ч")
    if bank_bonus > 0:
        text += f" (+{bank_bonus}% от бобров)\n"
    else:
        text += "\n"
    text += f"\nВыбери действие:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 Баланс", callback_data="bank_balance"),
        types.InlineKeyboardButton("📥 Положить", callback_data="bank_deposit"),
        types.InlineKeyboardButton("📤 Снять", callback_data="bank_withdraw"),
        types.InlineKeyboardButton("📜 История", callback_data="bank_history"),
        types.InlineKeyboardButton("🚪 Выход", callback_data="bank_exit")
    )
    bot.send_message(chat_id, text, reply_markup=markup)

def add_bank_history(user_id, operation):
    user = get_user(user_id)
    bank = user.get('bank', {'balance': 0, 'history': []})
    timestamp = time.strftime("%d.%m %H:%M")
    bank['history'].insert(0, f"{operation} — {timestamp}")
    bank['history'] = bank['history'][:10]
    user['bank'] = bank
    save_data()

# ====================== МАРКЕТ БОБРОВ ======================
def get_global_multiplier(user_id):
    user = get_user(user_id)
    beavers = user.get('beavers', {})
    mult = 1.0
    for beaver_id, count in beavers.items():
        if count > 0 and beaver_id in BEAVERS_DATA:
            if 'global_mult' in BEAVERS_DATA[beaver_id]:
                mult *= (BEAVERS_DATA[beaver_id]['global_mult'] ** count)
    return mult

def get_beaver_bonuses(user_id):
    # Заглушка, можно расширить
    return {}

def show_market_menu(chat_id, user_id):
    user = get_user(user_id)
    text = "🦫 Магазин коллекционных бобров\n\n"
    if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
        text += "🎉 ИВЕНТОВЫЙ БОБЁР В ПРОДАЖЕ! 🎉\n\n"
    text += "Каждый бобёр даёт множитель ко всем выигрышам:\n\n"
    for beaver_id, data in BEAVERS_DATA.items():
        available = data['total'] - data['sold']
        emoji = "✅" if available > 0 else "❌"
        text += f"{emoji} {data['name']}\n"
        text += f"└ Цена: {data['price']} кредиксов\n"
        text += f"└ Редкость: {data['rarity']}\n"
        text += f"└ {data['description']}\n"
        if 'global_mult' in data:
            text += f"└ Множитель: x{data['global_mult']}\n"
        text += f"└ Осталось: {available} шт.\n\n"
    text += f"\n💰 Твой баланс: {user['balance']} кредиксов\n"
    text += f"🦫 Твои бобры: {sum(user.get('beavers', {}).values())} шт.\n"
    text += f"📈 Твой общий множитель: x{get_global_multiplier(user_id):.2f}\n\n"
    text += "Выбери бобра для покупки:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    for beaver_id, data in BEAVERS_DATA.items():
        available = data['total'] - data['sold']
        if available > 0:
            btn_text = f"{data['name']} - {data['price']}💰"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"market_buy_{beaver_id}"))
    markup.add(types.InlineKeyboardButton("📊 Моя коллекция", callback_data="market_collection"))
    markup.add(types.InlineKeyboardButton("🚪 Выход", callback_data="market_exit"))
    bot.send_message(chat_id, text, reply_markup=markup)

def show_collection(chat_id, user_id):
    user = get_user(user_id)
    beavers = user.get('beavers', {})
    if not beavers:
        bot.send_message(chat_id, "🦫 У тебя пока нет бобров. Купи их в маркете!")
        return
    text = "📊 Твоя коллекция бобров:\n\n"
    for beaver_id, count in beavers.items():
        if count > 0 and beaver_id in BEAVERS_DATA:
            data = BEAVERS_DATA[beaver_id]
            text += f"🦫 {data['name']} — {count} шт.\n"
            text += f"└ Редкость: {data['rarity']}\n"
            text += f"└ {data['description']}\n"
            if 'global_mult' in data:
                text += f"└ Множитель: x{data['global_mult']}\n\n"
    text += f"📈 Твой общий множитель: x{get_global_multiplier(user_id):.2f}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Назад в маркет", callback_data="market_back"))
    bot.send_message(chat_id, text, reply_markup=markup)

def buy_beaver(user_id, beaver_id):
    user = get_user(user_id)
    if beaver_id not in BEAVERS_DATA:
        return False, "❌ Такого бобра не существует."
    beaver = BEAVERS_DATA[beaver_id]
    available = beaver['total'] - beaver['sold']
    if available <= 0:
        return False, f"❌ {beaver['name']} закончились!"
    if user['balance'] < beaver['price']:
        return False, f"❌ Недостаточно средств. Нужно: {beaver['price']} кредиксов."
    user['balance'] -= beaver['price']
    beaver['sold'] += 1
    if 'beavers' not in user:
        user['beavers'] = {}
    user['beavers'][beaver_id] = user['beavers'].get(beaver_id, 0) + 1
    save_data()
    return True, f"✅ Ты купил {beaver['name']} за {beaver['price']} кредиксов!"

# ====================== НОВЫЕ ФУНКЦИИ: ДОНАТ-ВАЛЮТА KRDS ======================

@bot.message_handler(commands=['донат'])
def donate_command(message):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    bot.send_message(message.chat.id, f"💎 Твой баланс KRDS: {user['krds_balance']}")

@bot.message_handler(commands=['сенд'])
def send_krds(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Использование: /сенд @username сумма")
            return
        target_username = parts[1].replace('@', '').lower()
        amount = parse_bet(parts[2])
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
            return
        target_id = username_cache.get(target_username)
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        if target_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя отправить самому себе.")
            return
        user = get_user(user_id)
        if user['krds_balance'] < amount:
            bot.send_message(message.chat.id, f"❌ Недостаточно KRDS. У тебя {user['krds_balance']}.")
            return
        target = get_user(target_id)
        user['krds_balance'] -= amount
        target['krds_balance'] += amount
        save_data()
        bot.send_message(message.chat.id, f"✅ Ты отправил {amount} KRDS пользователю @{target_username}.")
        try:
            bot.send_message(int(target_id), f"💰 Тебе отправили {amount} KRDS от @{message.from_user.username}.")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ====================== P2P ОБМЕННИК ======================

def update_treasury_rate():
    global TREASURY_RATE
    while True:
        time.sleep(60)
        with treasury_lock:
            TREASURY_RATE = random.randint(3000, 6500)
            save_data()

@bot.message_handler(commands=['обменник'])
def exchange_menu(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    text = "💱 P2P Обменник KRDS\n\n"
    text += f"💰 Курс казны: 1 KRDS = {TREASURY_RATE} кредиксов\n"
    text += "Ты можешь купить или продать KRDS по этому курсу напрямую у бота (казна), либо создать свой ордер.\n\n"
    text += "Выбери действие:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 Казна (купить/продать)", callback_data="exchange_treasury"),
        types.InlineKeyboardButton("📋 Мои ордера", callback_data="exchange_my_orders"),
        types.InlineKeyboardButton("🟢 Создать ордер на покупку", callback_data="exchange_create_buy"),
        types.InlineKeyboardButton("🔴 Создать ордер на продажу", callback_data="exchange_create_sell"),
        types.InlineKeyboardButton("📊 Все ордера", callback_data="exchange_all_orders"),
        types.InlineKeyboardButton("🚪 Закрыть", callback_data="exchange_exit")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('exchange_'))
def exchange_callback(call):
    user_id = str(call.from_user.id)
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "⛔ Вы забанены!")
        return
    data = call.data
    if data == 'exchange_treasury':
        text = f"💱 Казна\n\nКурс: 1 KRDS = {TREASURY_RATE} кредиксов\n\n"
        text += "Введи сумму KRDS для покупки или продажи через пробел и действие (buy/sell).\n"
        text += "Пример: `buy 10` — купить 10 KRDS\n"
        text += "Пример: `sell 5` — продать 5 KRDS"
        bot.send_message(call.message.chat.id, text)
        bot.answer_callback_query(call.id)
    elif data == 'exchange_my_orders':
        show_my_orders(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id)
    elif data == 'exchange_create_buy':
        msg = bot.send_message(call.message.chat.id, "Введи цену за 1 KRDS (от 100 до 100000) и сумму KRDS через пробел.\nПример: `5000 10`")
        bot.register_next_step_handler(msg, process_create_order, user_id, 'buy')
        bot.answer_callback_query(call.id)
    elif data == 'exchange_create_sell':
        msg = bot.send_message(call.message.chat.id, "Введи цену за 1 KRDS (от 100 до 100000) и сумму KRDS через пробел.\nПример: `5000 10`")
        bot.register_next_step_handler(msg, process_create_order, user_id, 'sell')
        bot.answer_callback_query(call.id)
    elif data == 'exchange_all_orders':
        show_all_orders(call.message.chat.id)
        bot.answer_callback_query(call.id)
    elif data == 'exchange_exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif data.startswith('order_take_'):
        parts = data.split('_')
        order_id = parts[2]
        take_order(user_id, call, order_id)

def process_create_order(message, user_id, order_type):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Неверный формат. Введи цену и сумму через пробел.")
            return
        price = int(parts[0])
        amount = int(parts[1])
        if price < 100 or price > 100000:
            bot.send_message(message.chat.id, "❌ Цена должна быть от 100 до 100000.")
            return
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
            return
        user = get_user(user_id)
        if order_type == 'sell':
            if user['krds_balance'] < amount:
                bot.send_message(message.chat.id, f"❌ Недостаточно KRDS. У тебя {user['krds_balance']}.")
                return
        else:  # buy
            total_cost = price * amount
            if user['balance'] < total_cost:
                bot.send_message(message.chat.id, f"❌ Недостаточно кредиксов. Нужно {total_cost}.")
                return
        # Создаём ордер
        global next_order_id
        order_id = str(next_order_id)
        next_order_id += 1
        orders[order_id] = {
            'user_id': user_id,
            'type': order_type,  # 'buy' или 'sell'
            'price': price,
            'amount': amount,
            'remaining': amount,
            'created': time.time()
        }
        save_data()
        bot.send_message(message.chat.id, f"✅ Ордер #{order_id} создан!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите числа.")

def show_my_orders(chat_id, user_id):
    my_orders = [o for o in orders.values() if o['user_id'] == user_id and o['remaining'] > 0]
    if not my_orders:
        bot.send_message(chat_id, "📋 У тебя нет активных ордеров.")
        return
    text = "📋 Твои активные ордера:\n\n"
    for oid, order in orders.items():
        if order['user_id'] == user_id and order['remaining'] > 0:
            text += f"#{oid}: {'🟢 Покупка' if order['type']=='buy' else '🔴 Продажа'} {order['remaining']} KRDS по {order['price']}💰\n"
    bot.send_message(chat_id, text)

def show_all_orders(chat_id):
    active_orders = {oid: o for oid, o in orders.items() if o['remaining'] > 0}
    if not active_orders:
        bot.send_message(chat_id, "📊 Нет активных ордеров.")
        return
    text = "📊 Все активные ордера:\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for oid, order in active_orders.items():
        try:
            user = bot.get_chat(int(order['user_id']))
            name = f"@{user.username}" if user.username else user.first_name
        except:
            name = f"ID {order['user_id']}"
        text += f"#{oid} {name}: {'🟢 Купить' if order['type']=='buy' else '🔴 Продать'} {order['remaining']} KRDS по {order['price']}💰\n"
        btn_text = f"#{oid} - {'Купить' if order['type']=='sell' else 'Продать'}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"order_take_{oid}"))
    bot.send_message(chat_id, text, reply_markup=markup)

def take_order(user_id, call, order_id):
    if order_id not in orders:
        bot.answer_callback_query(call.id, "❌ Ордер не найден.")
        return
    order = orders[order_id]
    if order['remaining'] <= 0:
        bot.answer_callback_query(call.id, "❌ Ордер уже исполнен.")
        return
    if order['user_id'] == user_id:
        bot.answer_callback_query(call.id, "❌ Нельзя взять свой ордер.")
        return
    user = get_user(user_id)
    creator = get_user(order['user_id'])
    if order['type'] == 'sell':  # creator продаёт, user покупает
        total_cost = order['price'] * order['remaining']
        if user['balance'] < total_cost:
            bot.answer_callback_query(call.id, f"❌ Недостаточно кредиксов. Нужно {total_cost}.")
            return
        # Проверяем, есть ли у creator KRDS
        if creator['krds_balance'] < order['remaining']:
            bot.answer_callback_query(call.id, "❌ У создателя ордера недостаточно KRDS.")
            # Удаляем ордер, так как он недействителен
            del orders[order_id]
            save_data()
            return
        # Выполняем сделку
        user['balance'] -= total_cost
        creator['balance'] += total_cost
        user['krds_balance'] += order['remaining']
        creator['krds_balance'] -= order['remaining']
        order['remaining'] = 0
        save_data()
        bot.answer_callback_query(call.id, f"✅ Ты купил {order['amount']} KRDS за {total_cost} кредиксов.")
        try:
            bot.send_message(int(order['user_id']), f"💰 Твой ордер #{order_id} на продажу KRDS исполнен! Ты получил {total_cost} кредиксов.")
        except:
            pass
    else:  # order['type'] == 'buy'  creator покупает, user продаёт
        total_cost = order['price'] * order['remaining']
        if user['krds_balance'] < order['remaining']:
            bot.answer_callback_query(call.id, f"❌ Недостаточно KRDS.")
            return
        if creator['balance'] < total_cost:
            bot.answer_callback_query(call.id, "❌ У создателя ордера недостаточно кредиксов.")
            # Удаляем ордер
            del orders[order_id]
            save_data()
            return
        user['krds_balance'] -= order['remaining']
        creator['krds_balance'] += order['remaining']
        user['balance'] += total_cost
        creator['balance'] -= total_cost
        order['remaining'] = 0
        save_data()
        bot.answer_callback_query(call.id, f"✅ Ты продал {order['amount']} KRDS за {total_cost} кредиксов.")
        try:
            bot.send_message(int(order['user_id']), f"💰 Твой ордер #{order_id} на покупку KRDS исполнен! Ты купил {order['amount']} KRDS.")
        except:
            pass

# ====================== КОМАНДА /ПОКУПКА ======================
@bot.message_handler(commands=['покупка'])
def purchase_info(message):
    bot.send_message(message.chat.id, 
                     "💫🎮 Привет! Для покупки донат-валюты KRDS напиши @kyniks.\n"
                     "Стоимость: 1 звезда = 5 KRDS 👾🎉")

# ====================== НОВЫЙ ЕЖЕДНЕВНЫЙ БОНУС ======================
@bot.message_handler(commands=['ежедневный'])
def new_daily_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    success, msg = claim_new_daily_bonus(user_id)
    bot.send_message(message.chat.id, msg)

# ====================== ИСТОРИЯ ИГР ======================
@bot.message_handler(commands=['история'])
def history_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    user = get_user(user_id)
    history = user.get('game_history', [])
    if not history:
        bot.send_message(message.chat.id, "📜 У тебя пока нет истории игр.")
        return
    text = "📜 Твоя последние игры:\n\n"
    for entry in history[:10]:
        dt = datetime.fromtimestamp(entry['time']).strftime('%d.%m %H:%M')
        sign = '+' if entry['win'] > 0 else '-'
        text += f"{dt} | {entry['game']} | Ставка: {entry['bet']} | {sign}{entry['win']} 💰\n"
    bot.send_message(message.chat.id, text)

# ====================== ЧЕКОВАЯ КНИЖКА ======================
@bot.message_handler(commands=['чек'])
def cheque_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    args = message.text.split()
    if len(args) == 1:
        bot.send_message(message.chat.id, 
                         "📒 Чековая книжка\n\n"
                         "Создать чек: /чек создать [сумма]\n"
                         "Активировать чек: /чек активировать [код]")
        return
    if args[1] == 'создать' and len(args) == 3:
        try:
            amount = parse_bet(args[2])
            if amount is None or amount <= 0:
                bot.send_message(message.chat.id, "❌ Неверная сумма.")
                return
            user = get_user(user_id)
            if user['balance'] < amount:
                bot.send_message(message.chat.id, f"❌ Недостаточно средств. Нужно {amount}.")
                return
            # Генерируем код
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while code in cheques:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            cheques[code] = {
                'creator': user_id,
                'amount': amount,
                'created': time.time(),
                'active': True
            }
            user['balance'] -= amount
            save_data()
            bot.send_message(message.chat.id, f"✅ Чек на {amount} кредиксов создан!\nКод: `{code}`\n"
                             f"Перешли этот код тому, кому хочешь подарить.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
    elif args[1] == 'активировать' and len(args) == 3:
        code = args[2].upper()
        if code not in cheques or not cheques[code].get('active', False):
            bot.send_message(message.chat.id, "❌ Чек не найден или уже активирован.")
            return
        cheque = cheques[code]
        if cheque['creator'] == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя активировать свой собственный чек.")
            return
        user = get_user(user_id)
        user['balance'] += cheque['amount']
        cheque['active'] = False
        save_data()
        bot.send_message(message.chat.id, f"✅ Чек активирован! Ты получил {cheque['amount']} кредиксов.")
        try:
            bot.send_message(int(cheque['creator']), f"🎉 Твой чек на {cheque['amount']} кредиксов был активирован!")
        except:
            pass
    else:
        bot.send_message(message.chat.id, "❌ Неверная команда. Используй /чек создать [сумма] или /чек активировать [код].")

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================
def show_ref_info(user_id, chat_id):
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    bonuses = get_beaver_bonuses(user_id)
    referral_bonus = bonuses.get('referral_bonus', 0)
    text = f"👥 Твоя реферальная ссылка:\n{ref_link}\n\n"
    text += f"📊 Приглашено друзей: {users[user_id]['referrals']}\n"
    text += f"🎁 За каждого друга ты получаешь 3000 кредиксов"
    if referral_bonus > 0:
        text += f" + {referral_bonus}% бонус от бобров"
    bot.send_message(chat_id, text)

def show_top(chat_id):
    sorted_users = sorted(
        [(str(k), v) for k, v in users.items()], 
        key=lambda x: x[1]['balance'], 
        reverse=True
    )[:10]
    if not sorted_users:
        bot.send_message(chat_id, "Пока нет пользователей в топе.")
        return
    text = "🏆 ТОП 10 ПО БАЛАНСУ:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = bot.get_chat(int(uid))
            name = user.first_name
            if user.username:
                name = f"@{user.username}"
                update_username_cache(int(uid), user.username)
        except:
            name = f"ID {uid}"
        beavers_count = sum(data.get('beavers', {}).values())
        text += f"{i}. 👤 {name} — 💰 {data['balance']} кредиксов (🦫 {beavers_count})\n"
    bot.send_message(chat_id, text)

def show_profile(chat_id, user_id):
    user = get_user(user_id)
    text = f"📱 Профиль игрока\n\n"
    text += f"👤 ID: {user_id}\n"
    text += f"💸 Баланс кредиксов: {user['balance']} 💫\n"
    text += f"💎 Баланс KRDS: {user['krds_balance']}\n"
    text += f"🎰 Проиграно кредиксов: {user.get('total_lost', 0)} 👾\n\n"
    text += "📊 Статистика игр:\n"
    text += f"🎮 Сыграно игр: {user.get('games_played', 0)}\n"
    text += f"✅ Побед: {user.get('total_wins', 0)}\n"
    text += f"❌ Поражений: {user.get('total_losses', 0)}\n"
    text += f"🔥 Текущий стрик: {user.get('win_streak', 0)}\n"
    text += f"🏆 Макс. стрик: {user.get('max_win_streak', 0)}\n\n"
    clan_name = user.get('clan')
    if clan_name and clan_name in clans:
        text += f"👥 Клан: {clan_name} (ур.{clans[clan_name]['level']})\n\n"
    if user_id in user_achievements:
        count = len(user_achievements[user_id])
        text += f"🏆 Достижений: {count}/{len(achievements)}\n\n"
    if user_id in event_data['participants']:
        text += f"🎉 Очков ивента: {event_data['participants'][user_id]['points']}\n\n"
    text += f"👥 Рефералов: {user.get('referrals', 0)}"
    bot.send_message(chat_id, text)

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds/60)} мин"
    elif seconds < 86400:
        return f"{int(seconds/3600)} ч"
    else:
        return f"{int(seconds/86400)} д"

def get_games_text():
    games_text = (
        "🎮 Список доступных игр и команд:\n\n"
        
        "🏰 Башня - 5 ячеек, выбирай ячейки\n"
        "   Команда: башня [ставка] (количество мин 1-3, по умолчанию 1)\n\n"
        
        "⚽ Футбол - Угадай, будет гол или мимо\n"
        "   Команда: футбол [ставка] [гол/мимо]\n\n"
        
        "🏀 Баскетбол - Угадай, попадёт или нет\n"
        "   Команда: баскетбол [ставка] [гол/мимо]\n\n"
        
        "🔺 Пирамида - 10 ячеек, одна мина\n"
        "   Команда: пирамида [ставка]\n\n"
        
        "💣 Мины - Поле 5x5\n"
        "   Команда: мины [ставка]\n\n"
        
        "🎰 Джекпот - Общий приз\n"
        "   Команда: джекпот [ставка]\n\n"
        
        "⚫️⚪️ Фишки - Угадай цвет\n"
        "   Команда: фишки [ставка] [black/white]\n\n"
        
        "🎲 X2/X3/X5 - Множители\n"
        "   Команда: x2 [ставка], x3 [ставка], x5 [ставка]\n\n"
        
        "🔫 Русская рулетка - Рискни (победа x1.75)\n"
        "   Команда: рулетка [ставка]\n\n"
        
        "🃏 Очко (21) - Карточная игра\n"
        "   Команда: очко [ставка]\n\n"
        
        "🚀 Краш - Ракета\n"
        "   Команда: краш [ставка]\n\n"
        
        "🎰 Слоты - Однорукий бандит\n"
        "   Команда: слоты [ставка]\n\n"
        
        "🎲 Кости - Бросай кости\n"
        "   Команда: кости [ставка] [тип] [значение]\n\n"
        
        "🎰 РУЛЕТКА - Европейская рулетка\n"
        "   Команда: рулетка [ставка]\n\n"
        
        "📈 Хило - Рискни!\n"
        "   Команда: хило [ставка] [low/medium/high]\n\n"
        
        "📦 Кейсы - Открывай кейсы\n"
        "   Команда: /кейсы или кнопка\n\n"
        
        "───────────── Дополнительно ─────────────\n"
        "💰 Баланс - /balance (или кнопка)\n"
        "👥 Рефералы - /реф\n"
        "🏆 Топ - /топ\n"
        "🏦 Банк - /банк\n"
        "🦫 Маркет - /маркет\n"
        "💼 Бизнес - /бизнесы\n"
        "👥 Клан - /клан\n"
        "⚔️ Дуэли - /дуэль @username ставка игра\n"
        "🏆 Достижения - /achievements\n"
        "📱 Профиль - /профиль\n"
        "💎 Бонус - /ежедневный\n"
        "📋 Задания - /задания\n"
        "🎉 Ивент - /ивент\n"
        "💎 Донат KRDS - /донат\n"
        "💱 Обменник KRDS - /обменник\n"
        "📜 История игр - /история\n"
        "📒 Чековая книжка - /чек\n"
        "💰 Перевод кредиксов - /дать @username сумма\n"
        "💸 Перевод KRDS - /сенд @username сумма\n"
        "🛑 Отмена игры - /cancel\n"
        "❓ Помощь - /help\n\n"
        
        f"👑 Владелец: {OWNER_USERNAME}\n"
        f"📢 Канал: {CHANNEL_USERNAME}\n"
        f"💬 Чат: {CHAT_LINK}"
    )
    return games_text

# ====================== БАЗОВЫЕ КОМАНДЫ ======================

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены и не можете использовать бота.")
        return
    args = message.text.split()
    if message.from_user.username:
        update_username_cache(message.from_user.id, message.from_user.username)
    if len(args) > 1 and args[1].isdigit():
        referrer_id = args[1]
        if referrer_id != user_id:
            user = get_user(user_id)
            if user['referrer'] is None:
                user['referrer'] = referrer_id
                if referrer_id in users:
                    users[referrer_id]['balance'] += 3000
                    users[referrer_id]['referrals'] += 1
                    try:
                        bot.send_message(int(referrer_id), 
                                       f"🎉 По твоей реферальной ссылке зарегистрировался новый пользователь!\n💰 Бонус: +3000 кредиксов!")
                    except:
                        pass
                save_data()
    user_name = message.from_user.first_name
    if message.from_user.username:
        user_name = f"@{message.from_user.username}"
    get_user(user_id)
    beavers_count = sum(users[user_id].get('beavers', {}).values())
    welcome_text = (
        f"👋 Привет, {user_name}!\n\n"
        f"👑 Владелец: {OWNER_USERNAME}\n"
        f"📢 Канал: {CHANNEL_USERNAME}\n"
        f"💬 Чат: {CHAT_LINK}\n\n"
        f"💸 Ваш баланс: {users[user_id]['balance']} кредиксов 💫\n"
        f"💎 Баланс KRDS: {users[user_id]['krds_balance']}\n"
        f"🎰 Проиграно кредиксов: {users[user_id].get('total_lost', 0)} 👾\n"
        f"🦫 Коллекция бобров: {beavers_count} шт.\n\n"
        f"🎮 Ознакомься с играми по команде /games или /игры\n"
    )
    if RELEASE_EVENT['active'] and time.time() < RELEASE_EVENT['end_time']:
        time_left = RELEASE_EVENT['end_time'] - time.time()
        days = int(time_left // 86400)
        hours = int((time_left % 86400) // 3600)
        welcome_text += f"\n🎉 ИВЕНТ В ЧЕСТЬ РЕЛИЗА! 🎉\n"
        welcome_text += f"⏱ До конца: {days}д {hours}ч\n"
        welcome_text += f"✨ Бонусы: x{RELEASE_EVENT['multiplier']} к выигрышам!\n"
    welcome_text += f"\n🎮 Выбери игру в меню ниже."
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(commands=['help', 'помощь'])
def help_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    bot.send_message(message.chat.id, get_games_text())

@bot.message_handler(commands=['games', 'game', 'игры'])
def games_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    bot.send_message(message.chat.id, get_games_text())

@bot.message_handler(commands=['cancel'])
def cancel_game(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    user = get_user(user_id)
    if user_id in crash_update_timers:
        crash_update_timers[user_id].cancel()
        del crash_update_timers[user_id]
    if user_id in game_timers:
        game_timers[user_id].cancel()
        del game_timers[user_id]
    if user['game'] is not None:
        if user['game'].get('stage') == 'waiting_bet' and 'bet' in user['game']:
            user['balance'] += user['game']['bet']
        user['game'] = None
        save_data()
        bot.send_message(message.chat.id, 
                        "🛑 Текущая игра отменена. Ставка возвращена (если была).", 
                        reply_markup=main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "У тебя нет активной игры.")

@bot.message_handler(commands=['balance', 'баланс'])
def balance_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    user = get_user(user_id)
    bot.send_message(message.chat.id, 
                    f"💸 Ваш баланс: {user['balance']} кредиксов 💫\n"
                    f"💎 Баланс KRDS: {user['krds_balance']}\n"
                    f"🎰 Проиграно кредиксов: {user.get('total_lost', 0)} 👾")

@bot.message_handler(commands=['кейсы'])
def cases_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    show_cases_menu(message.chat.id, user_id)

@bot.message_handler(commands=['achievements', 'достижения'])
def achievements_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    text = "🏆 Достижения\n\n"
    for ach_id, ach in achievements.items():
        unlocked = user_id in user_achievements and ach_id in user_achievements[user_id]
        status = "✅" if unlocked else "❌"
        text += f"{status} {ach['name']}\n"
        text += f"└ {ach['desc']}\n"
        text += f"└ Награда: {ach['reward']}💰\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['duel'])
def duel_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    args = message.text.split()
    if len(args) < 4:
        bot.send_message(message.chat.id, "❌ Использование: /duel @username ставка игра")
        return
    target = args[1].replace('@', '')
    try:
        bet = parse_bet(args[2])
        game = args[3]
        success, msg = create_duel(user_id, target, bet, game)
        bot.send_message(message.chat.id, msg)
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат")

@bot.message_handler(commands=['duel_accept'])
def duel_accept_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /duel_accept ID")
        return
    success, msg = accept_duel(user_id, args[1])
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['duel_decline'])
def duel_decline_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /duel_decline ID")
        return
    success, msg = decline_duel(user_id, args[1])
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['promo'])
def promo_command(message):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены и не можете использовать промокоды.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Использование: /promo код")
            return
        code = parts[1].upper()
        if code not in promocodes:
            bot.send_message(message.chat.id, "❌ Промокод не найден.")
            return
        if code in user.get('used_promos', []):
            bot.send_message(message.chat.id, "❌ Вы уже активировали этот промокод ранее.")
            return
        promo = promocodes[code]
        user['balance'] += promo['amount']
        if 'used_promos' not in user:
            user['used_promos'] = []
        user['used_promos'].append(code)
        del promocodes[code]
        save_data()
        bot.send_message(message.chat.id, 
                        f"🎁✅ Промокод активирован! Вы получили {promo['amount']} кредиксов.\n"
                        f"💰 Новый баланс: {user['balance']}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ====================== КОМАНДА /ДАТЬ (ПЕРЕВОД КРЕДИКСОВ) ======================
@bot.message_handler(commands=['дать'])
def give_command(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены.")
        return
    try:
        text = message.text.strip()
        parts = text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "❌ Использование:\n• /дать @username сумма\n• /дать сумма (ответом на сообщение)")
            return
        target_user_id = None
        amount = None
        if len(parts) == 3 and parts[1].startswith('@'):
            target_username = parts[1].replace('@', '').lower()
            amount = parse_bet(parts[2])
            if target_username in username_cache:
                target_user_id = username_cache[target_username]
            else:
                bot.send_message(message.chat.id, "❌ Пользователь не найден или не начинал диалог с ботом.")
                return
        elif len(parts) == 2 and message.reply_to_message:
            amount = parse_bet(parts[1])
            if message.reply_to_message.from_user:
                target_user_id = str(message.reply_to_message.from_user.id)
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной (можно использовать к и кк, например: 1000, 100к, 5кк).")
            return
        if target_user_id is None:
            bot.send_message(message.chat.id, "❌ Не удалось определить получателя. Укажи @username или ответь на сообщение.")
            return
        if target_user_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя перевести средства самому себе.")
            return
        bonuses = get_beaver_bonuses(user_id)
        effective_max_bet = MAX_BET * (1 + bonuses.get('max_bet_bonus', 0) / 100)
        if amount > effective_max_bet:
            bot.send_message(message.chat.id, f"❌ Максимальная сумма перевода с твоими бобрами: {int(effective_max_bet)}")
            return
        user = get_user(user_id)
        if user['balance'] < amount:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}")
            return
        user['balance'] -= amount
        users[target_user_id]['balance'] += amount
        save_data()
        sender_name = f"@{message.from_user.username}" if message.from_user.username else f"ID {message.from_user.id}"
        bot.send_message(message.chat.id, 
                        f"✅ Ты перевёл {amount} кредиксов пользователю {get_user_name(target_user_id)} 💸\n"
                        f"💰 Твой новый баланс: {user['balance']}")
        try:
            bot.send_message(int(target_user_id), 
                           f"💰 Тебе перевели {amount} кредиксов!\n"
                           f"👤 Отправитель: {sender_name}\n"
                           f"💰 Текущий баланс: {users[target_user_id]['balance']}")
        except Exception as e:
            print(f"Не удалось уведомить получателя: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

def get_user_name(user_id):
    try:
        user = bot.get_chat(int(user_id))
        if user.username:
            return f"@{user.username}"
        return user.first_name
    except:
        return f"ID {user_id}"

# ====================== КОМАНДЫ НА РУССКОМ (дополнительные) ======================

@bot.message_handler(commands=['задания'])
def quests_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_quests(message.chat.id, user_id)

@bot.message_handler(commands=['ивент'])
def event_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_event_menu(message.chat.id, user_id)

@bot.message_handler(commands=['маркет'])
def market_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_market_menu(message.chat.id, user_id)

@bot.message_handler(commands=['бонус'])
def bonus_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    success, msg = claim_new_daily_bonus(user_id)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['профиль'])
def profile_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_profile(message.chat.id, user_id)

@bot.message_handler(commands=['клан'])
def clan_command_ru(message):
    clan_command(message)

@bot.message_handler(commands=['бизнесы'])
def business_command_ru(message):
    business_command(message)

@bot.message_handler(commands=['реф'])
def ref_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_ref_info(user_id, message.chat.id)

@bot.message_handler(commands=['дуэль'])
def duel_command_ru(message):
    duel_command(message)

@bot.message_handler(commands=['банк'])
def bank_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    apply_bank_interest(user_id)
    show_bank_menu(message.chat.id, user_id)

@bot.message_handler(commands=['топ'])
def top_command_ru(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        return
    show_top(message.chat.id)

# ====================== АДМИН КОМАНДЫ ======================

@bot.message_handler(commands=['admin'])
def admin_login(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Использование: /admin пароль")
        return
    if args[1] == ADMIN_PASSWORD:
        admin_users.add(user_id)
        bot.send_message(message.chat.id, 
                        "🔑✅ Вы вошли в режим администратора!\n\n"
                        "📋 Доступные команды:\n"
                        "➕ /addbalance @username сумма — начислить кредиксы\n"
                        "💎 /addkrds @username сумма — начислить KRDS\n"
                        "🚫 /ban @username — забанить игрока\n"
                        "✅ /unban @username — разбанить\n"
                        "🎟 /createpromo сумма — создать промокод\n"
                        "🎉 /event_start — запустить ивент\n"
                        "🎉 /event_stop — остановить ивент\n"
                        "📊 /adminstats — статистика бота\n"
                        "🗑 /resetusers — сбросить всех пользователей\n"
                        "👥 /listusers [страница] — список пользователей\n"
                        "🚪 /admin_exit — выйти из админ-режима")
    else:
        bot.send_message(message.chat.id, "🔑❌ Неверный пароль!")

@bot.message_handler(commands=['admin_exit'])
def admin_exit(message):
    user_id = str(message.from_user.id)
    if user_id in admin_users:
        admin_users.remove(user_id)
        bot.send_message(message.chat.id, "👋 Вы вышли из режима администратора.")
    else:
        bot.send_message(message.chat.id, "❌ Вы не в режиме администратора.")

@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Использование: /addbalance @username сумма")
            return
        target_username = parts[1].replace('@', '').lower()
        amount = parse_bet(parts[2])
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной (можно использовать к и кк).")
            return
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        users[target_user]['balance'] += amount
        save_data()
        bot.send_message(message.chat.id, f"➕✅ Пользователю @{target_username} начислено {amount} кредиксов.")
        try:
            bot.send_message(int(target_user), f"💰 Вам начислено {amount} кредиксов администратором.")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Использование: /ban @username")
            return
        target_username = parts[1].replace('@', '').lower()
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        if target_user == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя забанить самого себя.")
            return
        users[target_user]['banned'] = True
        save_data()
        bot.send_message(message.chat.id, f"🔨✅ Пользователь @{target_username} забанен.")
        try:
            bot.send_message(int(target_user), "⛔ Вы были забанены администратором.")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Использование: /unban @username")
            return
        target_username = parts[1].replace('@', '').lower()
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        users[target_user]['banned'] = False
        save_data()
        bot.send_message(message.chat.id, f"✅ Пользователь @{target_username} разбанен.")
        try:
            bot.send_message(int(target_user), "✅ Вы были разбанены администратором.")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['createpromo'])
def create_promo(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Использование: /createpromo сумма")
            return
        amount = parse_bet(parts[1])
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной (можно использовать к и кк).")
            return
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while code in promocodes:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promocodes[code] = {
            'amount': amount,
            'created_by': user_id
        }
        save_data()
        bot.send_message(message.chat.id, 
                        f"🎟✅ Промокод создан!\n"
                        f"🔑 Код: {code}\n"
                        f"💰 Сумма: {amount} кредиксов")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['event_start'])
def event_start(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    global RELEASE_EVENT
    RELEASE_EVENT['active'] = True
    RELEASE_EVENT['start_time'] = time.time()
    RELEASE_EVENT['end_time'] = time.time() + 7 * 24 * 60 * 60
    if 'event_beaver' not in BEAVERS_DATA:
        BEAVERS_DATA['event_beaver'] = RELEASE_EVENT['special_shop']['event_beaver']
    save_data()
    bot.send_message(message.chat.id, 
                    "🎉 Ивент запущен!\n\n"
                    f"✨ Множитель: x{RELEASE_EVENT['multiplier']}\n"
                    f"📋 Бонус заданий: x{RELEASE_EVENT['bonus_quest_reward']}\n"
                    f"🦫 Ивентовый бобёр в маркете!\n"
                    f"🎉 Ивентовый кейс в разделе Кейсы\n"
                    f"⏱ Длительность: 7 дней")

@bot.message_handler(commands=['event_stop'])
def event_stop(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    global RELEASE_EVENT
    RELEASE_EVENT['active'] = False
    bot.send_message(message.chat.id, "⏹ Ивент остановлен")

@bot.message_handler(commands=['adminstats'])
def admin_stats(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    total_users = len(users)
    total_balance = sum(u['balance'] for u in users.values())
    total_bank = sum(u.get('bank', {}).get('balance', 0) for u in users.values())
    banned_count = sum(1 for u in users.values() if u.get('banned', False))
    total_promos = len(promocodes)
    total_beavers_sold = sum(b['sold'] for b in BEAVERS_DATA.values())
    total_beavers_revenue = sum(b['sold'] * b['price'] for b in BEAVERS_DATA.values())
    total_achievements = sum(len(ua) for ua in user_achievements.values())
    jackpot_amount = jackpot['total']
    total_duels = len(duels)
    total_quests_completed = sum(u.get('quests_completed', 0) for u in users.values())
    stats = (
        f"📊 Статистика бота\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"💰 Общий баланс: {total_balance} кредиксов\n"
        f"🏦 Общий банк: {total_bank} кредиксов\n"
        f"⛔ Забанено: {banned_count}\n"
        f"🎟 Активных промокодов: {total_promos}\n\n"
        f"🏆 Достижений получено: {total_achievements}\n"
        f"📋 Заданий выполнено: {total_quests_completed}\n"
        f"💰 Текущий джекпот: {jackpot_amount}\n"
        f"⚔️ Дуэлей: {total_duels}\n\n"
        f"🦫 Маркет бобров\n"
        f"📦 Продано бобров: {total_beavers_sold}\n"
        f"💵 Выручка: {total_beavers_revenue} кредиксов\n\n"
        f"🎉 Ивент\n"
        f"Активен: {'✅' if RELEASE_EVENT['active'] else '❌'}\n"
        f"Участников ивента: {len(event_data['participants'])}"
    )
    bot.send_message(message.chat.id, stats)

@bot.message_handler(commands=['addkrds'])
def add_krds(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Использование: /addkrds @username сумма")
            return
        target_username = parts[1].replace('@', '').lower()
        amount = parse_bet(parts[2])
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
            return
        target_user = username_cache.get(target_username)
        if not target_user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        users[target_user]['krds_balance'] += amount
        save_data()
        bot.send_message(message.chat.id, f"💎✅ Пользователю @{target_username} начислено {amount} KRDS.")
        try:
            bot.send_message(int(target_user), f"💎 Вам начислено {amount} KRDS администратором.")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['resetusers'])
def reset_users(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    for uid in list(users.keys()):
        users[uid] = {
            'balance': 1000,
            'krds_balance': 0,
            'game': None,
            'referrals': 0,
            'referrer': None,
            'banned': False,
            'bank': {'balance': 0, 'last_interest': time.time(), 'history': []},
            'beavers': {},
            'used_promos': [],
            'clan': None,
            'total_wins': 0,
            'total_losses': 0,
            'total_bets': 0,
            'games_played': 0,
            'win_streak': 0,
            'max_win_streak': 0,
            'total_lost': 0,
            'quests_completed': 0,
            'event_points': 0,
            'game_history': [],
            'daily_last_claim': 0,
            'daily_streak': 0,
            'last_case6_open': 0
        }
    global orders, next_order_id, cheques, jackpot, clans, businesses, user_achievements, user_quests, event_data, user_cases, duels
    orders = {}
    next_order_id = 1
    cheques = {}
    jackpot = {'total': 0, 'last_winner': None, 'last_win_time': None, 'history': []}
    clans = {}
    businesses = {}
    user_achievements = {}
    user_quests = {}
    event_data = {'active': RELEASE_EVENT['active'], 'participants': {}, 'leaderboard': [], 'last_update': time.time()}
    user_cases = {}
    duels = {}
    save_data()
    bot.send_message(message.chat.id, "✅ Все пользователи и данные сброшены.")

@bot.message_handler(commands=['listusers'])
def list_users(message):
    user_id = str(message.from_user.id)
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У вас нет прав администратора.")
        return
    args = message.text.split()
    page = 1
    if len(args) > 1:
        try:
            page = int(args[1])
        except:
            pass
    users_list = list(users.items())
    users_list.sort(key=lambda x: x[1]['balance'], reverse=True)
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    page_users = users_list[start:end]
    if not page_users:
        bot.send_message(message.chat.id, "❌ Нет пользователей на этой странице.")
        return
    text = f"👥 Список пользователей (страница {page}):\n\n"
    for uid, data in page_users:
        try:
            user = bot.get_chat(int(uid))
            name = f"@{user.username}" if user.username else user.first_name
        except:
            name = f"ID {uid}"
        text += f"{name} — 💰 {data['balance']} кредиксов, 💎 {data['krds_balance']} KRDS\n"
    bot.send_message(message.chat.id, text)

# ====================== ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ ======================

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = str(message.from_user.id)
    if is_banned(user_id):
        bot.send_message(message.chat.id, "⛔ Вы забанены и не можете использовать бота.")
        return
    user = get_user(user_id)
    text = message.text.strip()
    lower_text = text.lower()
    
    if message.from_user.username:
        update_username_cache(message.from_user.id, message.from_user.username)
    
    # Обработка активной игры (ожидание ставки)
    if user.get('game') and user['game'].get('stage') == 'waiting_bet':
        bet = parse_bet(text)
        if bet is None:
            clear_game(user_id)
            bot.send_message(message.chat.id, 
                            "⏹ Игра отменена, так как ты отправил не число. Ставка возвращена.",
                            reply_markup=main_menu_keyboard())
            return
        game_type = user['game']['type']
        try:
            if game_type == 'tower':
                mines = user['game'].get('mines', 1)
                start_tower_game(message, bet, mines)
            elif game_type == 'football':
                choice = text.lower()
                if choice not in ['гол', 'мимо']:
                    bot.send_message(message.chat.id, "❌ Выбери: гол или мимо")
                    return
                start_football_game(message, bet, choice)
            elif game_type == 'basketball':
                choice = text.lower()
                if choice not in ['гол', 'мимо']:
                    bot.send_message(message.chat.id, "❌ Выбери: гол или мимо")
                    return
                start_basketball_game(message, bet, choice)
            elif game_type == 'hilo':
                risk = text.lower()
                if risk not in ['low', 'medium', 'high']:
                    bot.send_message(message.chat.id, "❌ Выбери: low, medium, high")
                    return
                start_hilo_game(message, bet, risk)
            elif game_type == 'pyramid':
                start_pyramid_game(message, bet)
            elif game_type == 'mines':
                start_mines_game(message, bet)
            elif game_type == 'color':
                color = user['game'].get('color')
                start_color_game(message, bet, color)
            elif game_type == 'random_x':
                mult = user['game'].get('mult', 2)
                start_random_x_game(message, bet, mult)
            elif game_type == 'russian_roulette':
                start_russian_roulette_game(message, bet)
            elif game_type == 'blackjack':
                start_blackjack_game(message, bet)
            elif game_type == 'crash':
                start_crash_game(message, bet)
            elif game_type == 'slots':
                start_slots_game(message, bet)
            elif game_type == 'jackpot':
                start_jackpot_game(message, bet)
            elif game_type == 'dice':
                dice_type = user['game'].get('dice_type')
                dice_choice = user['game'].get('dice_choice')
                start_dice_game(message, bet, dice_type, dice_choice)
            elif game_type == 'roulette':
                if 'roulette_type' not in user['game']:
                    user['game']['bet'] = bet
                    save_data()
                    markup = get_roulette_bet_keyboard()
                    bot.send_message(message.chat.id,
                                    f"🎰 Рулетка\n\n"
                                    f"💰 Ставка: {bet} кредиксов\n"
                                    f"🎯 Выбери тип ставки:",
                                    reply_markup=markup)
                    return
                else:
                    bet_type = user['game']['roulette_type']
                    bet_value = user['game'].get('roulette_value')
                    start_roulette_game(message, bet, bet_type, bet_value)
            else:
                bot.send_message(message.chat.id, "❌ Неизвестный тип игры.")
                clear_game(user_id)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
            clear_game(user_id)
        return
    
    # Обработка банковских операций
    if user.get('game') and user['game'].get('type') == 'bank' and user['game'].get('stage') in ['deposit', 'withdraw']:
        try:
            amount = parse_bet(text)
            if amount is None:
                bot.send_message(message.chat.id, "❌ Введите число (можно использовать к и кк)")
                return
            action = user['game']['stage']
            if action == 'deposit':
                if amount > user['balance']:
                    bot.send_message(message.chat.id, f"❌ Недостаточно средств. Твой баланс: {user['balance']}.")
                    return
                user['balance'] -= amount
                user['bank']['balance'] += amount
                add_bank_history(user_id, f"📥 Пополнение +{amount}")
                bot.send_message(message.chat.id, f"✅ Ты положил {amount} кредиксов на депозит.")
            elif action == 'withdraw':
                bank_bal = user['bank']['balance']
                if amount > bank_bal:
                    bot.send_message(message.chat.id, f"❌ Недостаточно средств на депозите. Доступно: {bank_bal}.")
                    return
                user['bank']['balance'] -= amount
                user['balance'] += amount
                add_bank_history(user_id, f"📤 Снятие -{amount}")
                bot.send_message(message.chat.id, f"✅ Ты снял {amount} кредиксов с депозита.")
            save_data()
            apply_bank_interest(user_id)
            show_bank_menu(message.chat.id, user_id)
            user['game'] = None
            save_data()
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введите число.")
        return
    
    # Если сообщение начинается с /, пропускаем (обработано другими хендлерами)
    if message.text.startswith('/'):
        return
    
    # Обработка текстовых команд (без слеша) и кнопок
    if lower_text.startswith('башня '):
        try:
            parts = text.split()
            if len(parts) == 2:
                bet = parse_bet(parts[1])
                if bet is None:
                    bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                    return
                start_tower_game(message, bet, 1)
            elif len(parts) == 3:
                bet = parse_bet(parts[1])
                mines = int(parts[2])
                if bet is None or mines < 1 or mines > 3:
                    bot.send_message(message.chat.id, "❌ Неверная ставка или количество мин (1-3).")
                    return
                start_tower_game(message, bet, mines)
            else:
                bot.send_message(message.chat.id, "❌ Использование: башня [ставка] или башня [ставка] [мин 1-3]")
        except:
            bot.send_message(message.chat.id, "❌ Пример: башня 1000 или башня 1000 2")
    elif lower_text.startswith('футбол '):
        try:
            parts = text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Использование: футбол [ставка] [гол/мимо]")
                return
            bet = parse_bet(parts[1])
            choice = parts[2].lower()
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            if choice not in ['гол', 'мимо']:
                bot.send_message(message.chat.id, "❌ Выбери: гол или мимо")
                return
            start_football_game(message, bet, choice)
        except:
            bot.send_message(message.chat.id, "❌ Пример: футбол 1000 гол")
    elif lower_text.startswith('баскетбол '):
        try:
            parts = text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Использование: баскетбол [ставка] [гол/мимо]")
                return
            bet = parse_bet(parts[1])
            choice = parts[2].lower()
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            if choice not in ['гол', 'мимо']:
                bot.send_message(message.chat.id, "❌ Выбери: гол или мимо")
                return
            start_basketball_game(message, bet, choice)
        except:
            bot.send_message(message.chat.id, "❌ Пример: баскетбол 1000 гол")
    elif lower_text.startswith('хило '):
        try:
            parts = text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Использование: хило [ставка] [low/medium/high]")
                return
            bet = parse_bet(parts[1])
            risk = parts[2].lower()
            if bet is None or risk not in ['low', 'medium', 'high']:
                bot.send_message(message.chat.id, "❌ Неверная ставка или риск (low/medium/high).")
                return
            start_hilo_game(message, bet, risk)
        except:
            bot.send_message(message.chat.id, "❌ Пример: хило 1000 medium")
    elif lower_text.startswith('пирамида '):
        try:
            parts = text.split()
            if len(parts) != 2:
                bot.send_message(message.chat.id, "❌ Использование: пирамида [ставка]")
                return
            bet = parse_bet(parts[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            start_pyramid_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: пирамида 1000")
    elif lower_text in ['б', 'б/баланс', 'б баланс', '/balance', 'баланс']:
        user = get_user(user_id)
        bot.send_message(message.chat.id, 
                        f"💸 Ваш баланс: {user['balance']} кредиксов 💫\n"
                        f"🎰 Проиграно кредиксов: {user.get('total_lost', 0)} 👾")
    elif lower_text in ['реф', 'рефералы']:
        show_ref_info(user_id, message.chat.id)
    elif lower_text == 'топ':
        show_top(message.chat.id)
    elif lower_text.startswith('мины '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            start_mines_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: мины 1000 или мины 100к")
    elif lower_text.startswith('джекпот '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            start_jackpot_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: джекпот 1000 или джекпот 100к")
    elif lower_text.startswith('фишки '):
        try:
            parts = text.split()
            if len(parts) != 3:
                bot.send_message(message.chat.id, "❌ Использование: фишки [сумма] [black/white]")
                return
            bet = parse_bet(parts[1])
            color = parts[2].lower()
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            if color not in ['black', 'white']:
                bot.send_message(message.chat.id, "❌ Выбери: black (⚫️) или white (⚪️)")
                return
            start_color_game(message, bet, color)
        except:
            bot.send_message(message.chat.id, "❌ Пример: фишки 1000 black")
    elif lower_text.startswith('x2 '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            start_random_x_game(message, bet, 2)
        except:
            bot.send_message(message.chat.id, "❌ Пример: x2 1000")
    elif lower_text.startswith('x3 '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            start_random_x_game(message, bet, 3)
        except:
            bot.send_message(message.chat.id, "❌ Пример: x3 1000")
    elif lower_text.startswith('x5 '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            start_random_x_game(message, bet, 5)
        except:
            bot.send_message(message.chat.id, "❌ Пример: x5 1000")
    elif lower_text.startswith('рулетка '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            user['game'] = {'type': 'roulette', 'stage': 'waiting_bet', 'bet': bet}
            save_data()
            set_game_timer(user_id)
            markup = get_roulette_bet_keyboard()
            bot.send_message(message.chat.id, 
                            f"🎰 Рулетка\n\n"
                            f"💰 Ставка: {bet} кредиксов\n"
                            f"🎯 Выбери тип ставки:",
                            reply_markup=markup)
        except:
            bot.send_message(message.chat.id, "❌ Пример: рулетка 1000")
    elif lower_text.startswith('краш '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            start_crash_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: краш 1000, краш 100к, краш 5кк")
    elif lower_text.startswith('слоты '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            start_slots_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: слоты 1000")
    elif lower_text.startswith('очко '):
        try:
            bet = parse_bet(text.split()[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки. Используй число, 100к или 5кк")
                return
            start_blackjack_game(message, bet)
        except:
            bot.send_message(message.chat.id, "❌ Пример: очко 1000")
    elif lower_text.startswith('кости '):
        try:
            parts = text.split()
            if len(parts) < 3:
                bot.send_message(message.chat.id, "❌ Использование: кости [сумма] [тип] [значение]")
                return
            bet = parse_bet(parts[1])
            if bet is None:
                bot.send_message(message.chat.id, "❌ Неверный формат ставки.")
                return
            dice_type = parts[2].lower()
            if dice_type == 'число':
                if len(parts) != 4:
                    bot.send_message(message.chat.id, "❌ Для типа 'число' нужно указать число от 2 до 12")
                    return
                dice_choice = int(parts[3])
                if dice_choice < 2 or dice_choice > 12:
                    bot.send_message(message.chat.id, "❌ Число должно быть от 2 до 12")
                    return
                start_dice_game(message, bet, 'number', dice_choice)
            elif dice_type == 'чет':
                start_dice_game(message, bet, 'even_odd', 'even')
            elif dice_type == 'нечет':
                start_dice_game(message, bet, 'even_odd', 'odd')
            elif dice_type == 'больше':
                start_dice_game(message, bet, 'range', 'over7')
            elif dice_type == 'меньше':
                start_dice_game(message, bet, 'range', 'under7')
            else:
                bot.send_message(message.chat.id, "❌ Тип ставки: число, чет, нечет, больше, меньше")
        except:
            bot.send_message(message.chat.id, "❌ Пример: кости 1000 число 7")
    else:
        process_menu_button(message, text)

def process_menu_button(message, button_text):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    
    if button_text == '🏰 Башня':
        bot.send_message(message.chat.id, 
                        "🏰 Введи ставку (и количество мин 1-3 через пробел, если нужно):\n"
                        "Например: `1000` (1 мина) или `1000 2` (2 мины)\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'tower', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '⚽ Футбол':
        bot.send_message(message.chat.id, 
                        "⚽ Введи ставку и выбор (гол/мимо) через пробел:\n"
                        "Например: `1000 гол` или `1000 мимо`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'football', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🏀 Баскетбол':
        bot.send_message(message.chat.id, 
                        "🏀 Введи ставку и выбор (гол/мимо) через пробел:\n"
                        "Например: `1000 гол` или `1000 мимо`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'basketball', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '📈 Хило':
        bot.send_message(message.chat.id, 
                        "📈 Введи ставку и риск (low/medium/high) через пробел:\n"
                        "Например: `1000 medium`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'hilo', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🔺 Пирамида':
        bot.send_message(message.chat.id, 
                        "🔺 Введи ставку:\n"
                        "Например: `1000`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'pyramid', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '💣 Мины':
        bot.send_message(message.chat.id, 
                        "💣 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'mines', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🎰 Джекпот':
        bot.send_message(message.chat.id, 
                        "🎰 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'jackpot', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '⚫️⚪️ Фишки':
        bot.send_message(message.chat.id, 
                        "⚫️⚪️ Введи ставку и цвет через пробел:\n"
                        "Например: `1000 black` или `1000 white`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'color', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🎲 X2/X3/X5':
        bot.send_message(message.chat.id, 
                        "🎲 Введи ставку и множитель через пробел:\n"
                        "Например: `1000 x2`, `1000 x3`, `1000 x5`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'random_x', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🔫 Русская рулетка':
        bot.send_message(message.chat.id, 
                        "🔫 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'russian_roulette', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🃏 Очко (21)':
        bot.send_message(message.chat.id, 
                        "🃏 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'blackjack', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🚀 Краш':
        bot.send_message(message.chat.id, 
                        "🚀 Введи ставку:\n"
                        "Например: `1000`, `100к`, `5кк`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'crash', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🎰 Слоты':
        bot.send_message(message.chat.id, 
                        "🎰 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'slots', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🎲 Кости':
        bot.send_message(message.chat.id, 
                        "🎲 Введи ставку и тип ставки через пробел:\n"
                        "Типы: число [2-12], чет, нечет, больше, меньше\n"
                        "Например: `1000 число 7`, `1000 чет`, `1000 больше`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'dice', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '🎰 РУЛЕТКА':
        bot.send_message(message.chat.id, 
                        "🎰 Введи ставку:\n"
                        "Например: `1000` или `100к`\n"
                        "🚫 Для отмены введите /cancel")
        user['game'] = {'type': 'roulette', 'stage': 'waiting_bet'}
        save_data()
        set_game_timer(user_id)
    elif button_text == '📦 Кейсы':
        show_cases_menu(message.chat.id, user_id)
    else:
        pass

# ====================== ОБЩИЙ ОБРАБОТЧИК INLINE-КНОПОК ======================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "⛔ Вы забанены!")
        return
    user = get_user(user_id)
    data = call.data
    
    # Кейсы
    if data.startswith('case_open_'):
        case_id = data.replace('case_open_', '')
        success, msg = open_case(user_id, case_id)
        bot.answer_callback_query(call.id, msg)
        if success:
            show_cases_menu(call.message.chat.id, user_id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
    elif data == 'case_stats':
        show_case_stats(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id)
    elif data == 'case_exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # Игры
    elif data.startswith('football_'):
        parts = data.split('_')
        shot = parts[1]
        bet = int(parts[2])
        start_football_game(call.message, bet, shot)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif data.startswith('basketball_'):
        parts = data.split('_')
        shot = parts[1]
        bet = int(parts[2])
        start_basketball_game(call.message, bet, shot)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif data.startswith('hilo_'):
        parts = data.split('_')
        risk = parts[1]
        bet = int(parts[2])
        start_hilo_game(call.message, bet, risk)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif data.startswith('pyramid_cell_'):
        cell = int(data.split('_')[2])
        pyramid_cell_handler(user_id, call, cell)
    
    # Задания
    elif data.startswith('quest_claim_'):
        quest_id = data.replace('quest_claim_', '')
        success, msg = claim_quest_reward(user_id, quest_id)
        bot.answer_callback_query(call.id, msg)
        if success:
            show_quests(call.message.chat.id, user_id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
    elif data.startswith('quest_info_'):
        bot.answer_callback_query(call.id, "Задание уже выполнено и награда получена")
    
    # Ивент
    elif data == 'event_stats':
        if user_id in event_data['participants']:
            stats = event_data['participants'][user_id]
            text = (
                f"📊 Твоя статистика ивента\n\n"
                f"🎮 Сыграно игр: {stats['games_played']}\n"
                f"🏆 Побед: {stats['wins']}\n"
                f"💰 Выиграно: {stats['total_won']} кредиксов\n"
                f"⭐️ Очков ивента: {stats['points']}"
            )
        else:
            text = "📊 Ты пока не участвовал в ивенте. Сыграй в любую игру!"
        bot.send_message(call.message.chat.id, text)
        bot.answer_callback_query(call.id)
    elif data == 'event_prizes':
        text = (
            "🎁 Призы ивента\n\n"
            "🥇 1 место: 500,000 кредиксов + 🦫 Ивентовый бобёр\n"
            "🥈 2 место: 300,000 кредиксов\n"
            "🥉 3 место: 200,000 кредиксов\n"
            "4-10 место: 50,000 кредиксов\n\n"
            "Итоги будут подведены после завершения ивента!"
        )
        bot.send_message(call.message.chat.id, text)
        bot.answer_callback_query(call.id)
    
    # Мины
    elif data.startswith('mines_count_'):
        mines = int(data.split('_')[2])
        game = user.get('game')
        if game and game['type'] == 'mines' and game['stage'] == 'choosing_mines_count':
            cells = list(range(1, 26))
            random.shuffle(cells)
            mine_positions = set(cells[:mines])
            game['mines'] = list(mine_positions)
            game['opened'] = []
            game['stage'] = 'playing_mines'
            save_data()
            show_mines_field(call.message.chat.id, game)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif data.startswith('mines_cell_'):
        cell = int(data.split('_')[2])
        game = user.get('game')
        if game and game['type'] == 'mines' and game['stage'] == 'playing_mines':
            if cell in game['opened']:
                bot.answer_callback_query(call.id, "❌ Ячейка уже открыта")
                return
            if cell in game['mines']:
                bot.edit_message_text(
                    f"💥 Ты наступил на мину! Ты проиграл {game['bet']} кредиксов.\n💰 Баланс: {user['balance']}",
                    call.message.chat.id,
                    call.message.message_id
                )
                user['total_losses'] = user.get('total_losses', 0) + 1
                user['win_streak'] = 0
                user['total_lost'] = user.get('total_lost', 0) + game['bet']
                update_event_stats(user_id, 'mines', 0)
                add_game_history(user_id, '💣 Мины', game['bet'], 0, 'lose')
                clear_game(user_id)
                save_data()
                bot.answer_callback_query(call.id, "💥 Ты проиграл!")
            else:
                game['opened'].append(cell)
                save_data()
                mines_count = len(game['mines'])
                opened_count = len(game['opened'])
                safe_count = 25 - mines_count
                if opened_count == safe_count:
                    current_mult = MINES_MULTIPLIERS[mines_count][safe_count]
                    win = int(game['bet'] * current_mult * get_global_multiplier(user_id) * get_event_multiplier())
                    user['balance'] += win
                    user['total_wins'] = user.get('total_wins', 0) + 1
                    user['win_streak'] = user.get('win_streak', 0) + 1
                    user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
                    update_quest_progress(user_id, 'win', 1)
                    update_quest_progress(user_id, 'earn', win // 1000)
                    update_event_stats(user_id, 'mines', win)
                    add_game_history(user_id, '💣 Мины', game['bet'], win, 'win')
                    save_data()
                    bot.edit_message_text(
                        f"🎉 Ты открыл все безопасные ячейки!\n"
                        f"Множитель: x{current_mult:.2f}\n"
                        f"💰 Ты выиграл {win} кредиксов!\n"
                        f"💰 Новый баланс: {user['balance']}",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    clear_game(user_id)
                    bot.answer_callback_query(call.id, "🎉 Ты выиграл!")
                else:
                    show_mines_field(call.message.chat.id, game)
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.answer_callback_query(call.id, "✅ Ячейка безопасна!")
    elif data == 'mines_take':
        game = user.get('game')
        if game and game['type'] == 'mines' and game['stage'] == 'playing_mines':
            mines_count = len(game['mines'])
            opened_count = len(game['opened'])
            if opened_count == 0:
                bot.answer_callback_query(call.id, "❌ Ты ещё не открыл ни одной ячейки!")
                return
            if opened_count in MINES_MULTIPLIERS[mines_count]:
                current_mult = MINES_MULTIPLIERS[mines_count][opened_count]
            else:
                max_opened = max(MINES_MULTIPLIERS[mines_count].keys())
                current_mult = MINES_MULTIPLIERS[mines_count][max_opened]
            win = int(game['bet'] * current_mult * get_global_multiplier(user_id) * get_event_multiplier())
            user['balance'] += win
            user['total_wins'] = user.get('total_wins', 0) + 1
            user['win_streak'] = user.get('win_streak', 0) + 1
            user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
            update_quest_progress(user_id, 'win', 1)
            update_quest_progress(user_id, 'earn', win // 1000)
            update_event_stats(user_id, 'mines', win)
            add_game_history(user_id, '💣 Мины', game['bet'], win, 'win')
            save_data()
            bot.edit_message_text(
                f"✅ Ты забрал выигрыш!\n"
                f"Множитель: x{current_mult:.2f}\n"
                f"💰 Ты выиграл {win} кредиксов!\n"
                f"💰 Новый баланс: {user['balance']}",
                call.message.chat.id,
                call.message.message_id
            )
            clear_game(user_id)
            bot.answer_callback_query(call.id, f"🎉 Ты выиграл {win}!")
    
    # Башня
    elif data.startswith('tower_cell_'):
        cell = int(data.split('_')[2])
        tower_cell_handler(user_id, call, cell)
    elif data == 'tower_take':
        tower_take_handler(user_id, call)
    elif data == 'tower_continue':
        game = user.get('game')
        if game and game['type'] == 'tower' and game['stage'] == 'playing_tower':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            show_tower_field(call.message.chat.id, game)
            bot.answer_callback_query(call.id)
    
    # Краш
    elif data == 'crash_take':
        crash_take_win(user_id, call)
    
    # 21
    elif data in ['21_hit', '21_stand']:
        game = user.get('game')
        if game and game['type'] == 'blackjack' and game['stage'] == 'playing_21':
            bet = game['bet']
            player_hand = game['player_hand']
            dealer_hand = game['dealer_hand']
            if data == '21_hit':
                new_card = get_card()
                player_hand.append(new_card)
                player_sum = calc_hand(player_hand)
                dealer_visible = dealer_hand[0]
                if player_sum > 21:
                    user['total_losses'] = user.get('total_losses', 0) + 1
                    user['win_streak'] = 0
                    user['total_lost'] = user.get('total_lost', 0) + bet
                    update_event_stats(user_id, 'blackjack', 0)
                    add_game_history(user_id, '🃏 Очко', bet, 0, 'lose')
                    clear_game(user_id)
                    save_data()
                    bot.edit_message_text(
                        f"❌ Перебор! Ты набрал {player_sum}. Ты проиграл {bet} кредиксов.\n💰 Баланс: {user['balance']}",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    bot.answer_callback_query(call.id, "💥 Перебор!")
                    return
                else:
                    game['player_hand'] = player_hand
                    save_data()
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        types.InlineKeyboardButton("🎴 Ещё", callback_data="21_hit"),
                        types.InlineKeyboardButton("🛑 Хватит", callback_data="21_stand")
                    )
                    msg = (f"🃏 Очко (21)\n\n"
                           f"💰 Ставка: {bet} кредиксов\n"
                           f"👤 Твои карты: {hand_to_str(player_hand)} = {player_sum}\n"
                           f"🤵 Карта дилера: {dealer_visible}\n\n"
                           f"Выбери действие:")
                    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                                         reply_markup=markup)
                    bot.answer_callback_query(call.id)
                    return
            elif data == '21_stand':
                dealer_sum = calc_hand(dealer_hand)
                while dealer_sum < 17:
                    dealer_hand.append(get_card())
                    dealer_sum = calc_hand(dealer_hand)
                player_sum = calc_hand(player_hand)
                if dealer_sum > 21:
                    win = int(bet * BLACKJACK_MULTIPLIER * get_global_multiplier(user_id) * get_event_multiplier())
                    user['balance'] += win
                    result_text = (f"🎉 Дилер перебрал! Ты выиграл {win} кредиксов (x{BLACKJACK_MULTIPLIER})!\n"
                                   f"💰 Новый баланс: {user['balance']}")
                    user['total_wins'] = user.get('total_wins', 0) + 1
                    user['win_streak'] = user.get('win_streak', 0) + 1
                    update_event_stats(user_id, 'blackjack', win)
                    add_game_history(user_id, '🃏 Очко', bet, win, 'win')
                elif player_sum > dealer_sum:
                    win = int(bet * BLACKJACK_MULTIPLIER * get_global_multiplier(user_id) * get_event_multiplier())
                    user['balance'] += win
                    result_text = (f"🎉 Ты набрал больше дилера! Ты выиграл {win} кредиксов (x{BLACKJACK_MULTIPLIER})!\n"
                                   f"💰 Новый баланс: {user['balance']}")
                    user['total_wins'] = user.get('total_wins', 0) + 1
                    user['win_streak'] = user.get('win_streak', 0) + 1
                    update_event_stats(user_id, 'blackjack', win)
                    add_game_history(user_id, '🃏 Очко', bet, win, 'win')
                elif player_sum < dealer_sum:
                    result_text = f"❌ Дилер набрал больше. Ты проиграл {bet} кредиксов.\n💰 Баланс: {user['balance']}"
                    user['total_losses'] = user.get('total_losses', 0) + 1
                    user['win_streak'] = 0
                    user['total_lost'] = user.get('total_lost', 0) + bet
                    update_event_stats(user_id, 'blackjack', 0)
                    add_game_history(user_id, '🃏 Очко', bet, 0, 'lose')
                else:
                    user['balance'] += bet
                    result_text = f"🤝 Ничья! Ставка возвращена.\n💰 Баланс: {user['balance']}"
                    add_game_history(user_id, '🃏 Очко', bet, bet, 'draw')
                user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
                save_data()
                dealer_cards_str = hand_to_str(dealer_hand)
                msg = (f"🃏 Очко (21)\n\n"
                       f"👤 Твои карты: {hand_to_str(player_hand)} = {player_sum}\n"
                       f"🤵 Карты дилера: {dealer_cards_str} = {dealer_sum}\n\n"
                       f"{result_text}")
                bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
                clear_game(user_id)
                bot.answer_callback_query(call.id)
    
    # Рулетка
    elif data.startswith('roulette_number_'):
        game = user.get('game')
        if game and game['type'] == 'roulette' and game.get('stage') == 'choosing_roulette_number':
            bet = game['bet']
            chosen_number = int(data.replace('roulette_number_', ''))
            number, color = roulette_spin()
            win, mult = roulette_result(bet, 'straight', chosen_number, number, color)
            if win > 0:
                win = int(win * get_global_multiplier(user_id) * get_event_multiplier())
                user['balance'] += win
                user['total_wins'] = user.get('total_wins', 0) + 1
                user['win_streak'] = user.get('win_streak', 0) + 1
                update_quest_progress(user_id, 'win', 1)
                update_quest_progress(user_id, 'earn', win // 1000)
                update_event_stats(user_id, 'roulette', win)
                result_text = f"🎉 Выпало {number} {get_color_emoji(color)}! Ты выиграл {win} кредиксов"
                if mult > 0:
                    result_text += f" (x{mult})"
                add_game_history(user_id, '🎰 Рулетка', bet, win, 'win')
            else:
                result_text = f"❌ Выпало {number} {get_color_emoji(color)}. Ты проиграл {bet} кредиксов."
                user['total_losses'] = user.get('total_losses', 0) + 1
                user['win_streak'] = 0
                user['total_lost'] = user.get('total_lost', 0) + bet
                update_event_stats(user_id, 'roulette', 0)
                add_game_history(user_id, '🎰 Рулетка', bet, 0, 'lose')
            user['max_win_streak'] = max(user.get('max_win_streak', 0), user['win_streak'])
            save_data()
            result_text += f"\n💰 Новый баланс: {user['balance']}"
            bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id)
            clear_game(user_id)
            bot.answer_callback_query(call.id)
        
        
                win = int(win * get_global_multiplier(user_id) * get_event_multiplier())
