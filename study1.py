"""
龙之传说 - 文字冒险游戏
一个完整的RPG风格文字游戏，包含多个系统
"""

import random
import time
import sys
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


# ==================== 游戏配置 ====================
class GameConfig:
    """游戏配置类"""
    VERSION = "1.0.0"
    GAME_NAME = "龙之传说"
    AUTHOR = "Python游戏开发者"

    # 游戏难度设置
    DIFFICULTY = {
        "easy": {"enemy_hp_mult": 0.7, "player_hp_mult": 1.3, "xp_mult": 1.2},
        "normal": {"enemy_hp_mult": 1.0, "player_hp_mult": 1.0, "xp_mult": 1.0},
        "hard": {"enemy_hp_mult": 1.5, "player_hp_mult": 0.8, "xp_mult": 0.8}
    }

    # 游戏区域
    REGIONS = ["新手村", "幽暗森林", "荒芜山脉", "诅咒沼泽", "巨龙巢穴"]

    # 颜色代码 (终端中使用)
    class Colors:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'


# ==================== 枚举类型 ====================
class ItemType(Enum):
    """物品类型枚举"""
    WEAPON = "武器"
    ARMOR = "护甲"
    POTION = "药水"
    QUEST = "任务物品"
    MATERIAL = "材料"
    TREASURE = "宝藏"


class EnemyType(Enum):
    """敌人类型枚举"""
    GOBLIN = "哥布林"
    WOLF = "野狼"
    ORC = "兽人"
    TROLL = "巨魔"
    DRAGON = "龙"
    SLIME = "史莱姆"
    SKELETON = "骷髅"
    WIZARD = "邪恶法师"


class QuestStatus(Enum):
    """任务状态枚举"""
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    FAILED = "失败"


# ==================== 数据类 ====================
@dataclass
class Item:
    """物品类"""
    id: int
    name: str
    description: str
    item_type: ItemType
    value: int  # 对于装备是攻击/防御值，对于药水是恢复量
    price: int
    usable: bool = True
    equipped: bool = False

    def __str__(self):
        color = GameConfig.Colors.GREEN if self.equipped else GameConfig.Colors.WHITE
        return f"{color}{self.name}{GameConfig.Colors.END} - {self.description} ({self.item_type.value})"


@dataclass
class Enemy:
    """敌人类"""
    id: int
    name: str
    enemy_type: EnemyType
    level: int
    health: int
    max_health: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int
    description: str

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 2)
        self.health -= actual_damage
        return actual_damage

    def __str__(self):
        health_percent = (self.health / self.max_health) * 100
        if health_percent > 70:
            health_color = GameConfig.Colors.GREEN
        elif health_percent > 30:
            health_color = GameConfig.Colors.YELLOW
        else:
            health_color = GameConfig.Colors.RED

        return f"{health_color}{self.name} (Lv.{self.level}){GameConfig.Colors.END} - HP: {self.health}/{self.max_health}"


@dataclass
class Quest:
    """任务类"""
    id: int
    name: str
    description: str
    requirements: Dict[str, int]  # 需要击杀的敌人类型和数量
    reward_xp: int
    reward_gold: int
    reward_items: List[int]  # 物品ID列表
    status: QuestStatus = QuestStatus.NOT_STARTED
    progress: Dict[str, int] = None

    def __post_init__(self):
        if self.progress is None:
            self.progress = {key: 0 for key in self.requirements.keys()}

    def update_progress(self, enemy_type):
        """更新任务进度"""
        enemy_name = enemy_type.value
        if enemy_name in self.progress:
            self.progress[enemy_name] += 1

    def is_completed(self):
        """检查任务是否完成"""
        for enemy_type, required in self.requirements.items():
            if self.progress.get(enemy_type, 0) < required:
                return False
        return True

    def __str__(self):
        status_color = GameConfig.Colors.GREEN if self.status == QuestStatus.COMPLETED else GameConfig.Colors.YELLOW
        return f"{status_color}[{self.status.value}]{GameConfig.Colors.END} {self.name}: {self.description}"


# ==================== 玩家类 ====================
class Player:
    """玩家类"""

    def __init__(self, name, difficulty="normal"):
        self.name = name
        self.difficulty = difficulty

        # 基础属性
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # 战斗属性
        diff_mult = GameConfig.DIFFICULTY[difficulty]
        base_hp = 100 * diff_mult["player_hp_mult"]
        self.health = base_hp
        self.max_health = base_hp
        self.base_attack = 10
        self.base_defense = 5

        # 装备属性
        self.weapon = None
        self.armor = None

        # 资源
        self.gold = 50
        self.inventory = []

        # 任务相关
        self.quests = []
        self.completed_quests = []

        # 游戏进度
        self.current_region = "新手村"
        self.regions_visited = ["新手村"]
        self.enemies_defeated = {}

        # 初始化物品
        self._initialize_starting_items()

    def _initialize_starting_items(self):
        """初始化起始物品"""
        starting_items = [
            Item(1, "木剑", "一把简单的木剑", ItemType.WEAPON, 3, 10),
            Item(2, "布甲", "简单的布制护甲", ItemType.ARMOR, 2, 15),
            Item(3, "小生命药水", "恢复30点生命值", ItemType.POTION, 30, 20),
            Item(4, "小生命药水", "恢复30点生命值", ItemType.POTION, 30, 20)
        ]

        self.inventory.extend(starting_items)
        self.equip_item(starting_items[0])  # 装备木剑
        self.equip_item(starting_items[1])  # 装备布甲

    @property
    def attack(self):
        """计算总攻击力"""

        weapon_attack = self.weapon.value if self.weapon else 0
        return self.base_attack + weapon_attack

    @property
    def defense(self):
        """计算总防御力"""
        armor_defense = self.armor.value if self.armor else 0
        return self.base_defense + armor_defense

    def take_damage(self, damage):
        """玩家受到伤害"""
        actual_damage = max(1, damage - self.defense // 3)
        self.health -= actual_damage
        return actual_damage

    def heal(self, amount):
        """治疗玩家"""
        self.health = min(self.max_health, self.health + amount)
        return amount

    def add_xp(self, xp_amount):
        """增加经验值"""
        diff_mult = GameConfig.DIFFICULTY[self.difficulty]
        xp_amount = int(xp_amount * diff_mult["xp_mult"])

        self.xp += xp_amount

        # 检查升级
        levels_gained = 0
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up()
            levels_gained += 1

        return xp_amount, levels_gained

    def level_up(self):
        """升级玩家"""
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.base_attack += 3
        self.base_defense += 2
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)

        print(f"\n{GameConfig.Colors.CYAN}★ 恭喜升级！现在是 {self.level} 级！{GameConfig.Colors.END}")
        print(f"最大生命值: +20, 攻击力: +3, 防御力: +2")

    def add_gold(self, amount):
        """增加金币"""
        self.gold += amount
        return self.gold

    def add_item(self, item):
        """添加物品到背包"""
        self.inventory.append(item)

    def remove_item(self, item):
        """从背包移除物品"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def equip_item(self, item):
        """装备物品"""
        if item not in self.inventory:
            return False

        if item.item_type == ItemType.WEAPON:
            # 卸下当前武器
            if self.weapon:
                self.weapon.equipped = False
            # 装备新武器
            self.weapon = item
            item.equipped = True
            return True

        elif item.item_type == ItemType.ARMOR:
            # 卸下当前护甲
            if self.armor:
                self.armor.equipped = False
            # 装备新护甲
            self.armor = item
            item.equipped = True
            return True

        return False

    def unequip_item(self, item_type):
        """卸下装备"""
        if item_type == ItemType.WEAPON and self.weapon:
            self.weapon.equipped = False
            self.weapon = None
            return True
        elif item_type == ItemType.ARMOR and self.armor:
            self.armor.equipped = False
            self.armor = None
            return True
        return False

    def use_item(self, item):
        """使用物品"""
        if item.item_type == ItemType.POTION:
            amount_healed = self.heal(item.value)
            print(f"使用了{item.name}，恢复了{amount_healed}点生命值")
            self.remove_item(item)
            return True
        return False

    def add_quest(self, quest):
        """接受任务"""
        quest.status = QuestStatus.IN_PROGRESS
        self.quests.append(quest)

    def complete_quest(self, quest):
        """完成任务"""
        if quest in self.quests:
            quest.status = QuestStatus.COMPLETED
            self.quests.remove(quest)
            self.completed_quests.append(quest)

            # 给予奖励
            self.add_xp(quest.reward_xp)
            self.add_gold(quest.reward_gold)

            print(f"\n{GameConfig.Colors.GREEN}✓ 任务完成: {quest.name}{GameConfig.Colors.END}")
            print(f"获得 {quest.reward_xp} 经验值")
            print(f"获得 {quest.reward_gold} 金币")

            return True
        return False

    def update_quest_progress(self, enemy_type):
        """更新所有任务进度"""
        for quest in self.quests:
            quest.update_progress(enemy_type)

    def record_enemy_defeat(self, enemy_name):
        """记录击败的敌人"""
        self.enemies_defeated[enemy_name] = self.enemies_defeated.get(enemy_name, 0) + 1

    def move_to_region(self, region_name):
        """移动到新区域"""
        if region_name not in self.regions_visited:
            self.regions_visited.append(region_name)
        self.current_region = region_name

    def get_status(self):
        """获取玩家状态字符串"""
        health_percent = (self.health / self.max_health) * 100
        if health_percent > 70:
            health_color = GameConfig.Colors.GREEN
        elif health_percent > 30:
            health_color = GameConfig.Colors.YELLOW
        else:
            health_color = GameConfig.Colors.RED

        return (
            f"{GameConfig.Colors.BOLD}{self.name}{GameConfig.Colors.END} "
            f"(Lv.{self.level}) - "
            f"{health_color}HP: {self.health}/{self.max_health}{GameConfig.Colors.END} | "
            f"攻击: {self.attack} | 防御: {self.defense} | "
            f"金币: {self.gold} | 区域: {self.current_region}"
        )


# ==================== 游戏世界类 ====================
class GameWorld:
    """游戏世界类"""

    def __init__(self):
        self.regions = {}
        self.enemies = {}
        self.items = {}
        self.quests = {}
        self.shops = {}

        self._initialize_world()

    def _initialize_world(self):
        """初始化游戏世界"""
        self._initialize_items()
        self._initialize_enemies()
        self._initialize_quests()
        self._initialize_shops()
        self._initialize_regions()

    def _initialize_items(self):
        """初始化所有物品"""
        # 武器
        self.items[1] = Item(1, "木剑", "一把简单的木剑", ItemType.WEAPON, 3, 10)
        self.items[2] = Item(2, "铁剑", "一把锋利的铁剑", ItemType.WEAPON, 8, 50)
        self.items[3] = Item(3, "钢剑", "精钢打造的长剑", ItemType.WEAPON, 15, 150)
        self.items[4] = Item(4, "龙息剑", "蕴含龙之力的宝剑", ItemType.WEAPON, 25, 500)

        # 护甲
        self.items[5] = Item(5, "布甲", "简单的布制护甲", ItemType.ARMOR, 2, 15)
        self.items[6] = Item(6, "皮甲", "坚韧的皮革护甲", ItemType.ARMOR, 5, 60)
        self.items[7] = Item(7, "锁子甲", "金属环编织的护甲", ItemType.ARMOR, 10, 200)
        self.items[8] = Item(8, "龙鳞甲", "用龙鳞制成的护甲", ItemType.ARMOR, 18, 600)

        # 药水
        self.items[9] = Item(9, "小生命药水", "恢复30点生命值", ItemType.POTION, 30, 20)
        self.items[10] = Item(10, "中生命药水", "恢复60点生命值", ItemType.POTION, 60, 40)
        self.items[11] = Item(11, "大生命药水", "恢复100点生命值", ItemType.POTION, 100, 80)
        self.items[12] = Item(12, "生命灵药", "恢复全部生命值", ItemType.POTION, 999, 200)

        # 任务物品
        self.items[13] = Item(13, "哥布林耳朵", "证明击败哥布林的凭证", ItemType.QUEST, 0, 1, False)
        self.items[14] = Item(14, "野狼皮毛", "野狼的皮毛", ItemType.QUEST, 0, 5, False)
        self.items[15] = Item(15, "龙之宝玉", "传说中龙守护的宝石", ItemType.QUEST, 0, 1000, False)

        # 宝藏
        self.items[16] = Item(16, "金项链", "价值不菲的金项链", ItemType.TREASURE, 0, 100)
        self.items[17] = Item(17, "古金币", "古代王国流通的金币", ItemType.TREASURE, 0, 50)
        self.items[18] = Item(18, "魔法水晶", "蕴含魔法能量的水晶", ItemType.TREASURE, 0, 200)

    def _initialize_enemies(self):
        """初始化所有敌人"""
        # 新手村敌人
        self.enemies[1] = Enemy(1, "弱小哥布林", EnemyType.GOBLIN, 1, 30, 30, 5, 2, 10, 5,
                                "新手村常见的弱小敌人")
        self.enemies[2] = Enemy(2, "野生小狼", EnemyType.WOLF, 1, 25, 25, 7, 1, 8, 3,
                                "游荡在野外的狼")

        # 幽暗森林敌人
        self.enemies[3] = Enemy(3, "哥布林战士", EnemyType.GOBLIN, 3, 60, 60, 10, 4, 25, 15,
                                "装备简陋武器的哥布林")
        self.enemies[4] = Enemy(4, "野狼", EnemyType.WOLF, 3, 50, 50, 12, 3, 20, 10,
                                "成年的野狼")
        self.enemies[5] = Enemy(5, "绿色史莱姆", EnemyType.SLIME, 2, 40, 40, 8, 0, 15, 8,
                                "粘稠的绿色凝胶状生物")

        # 荒芜山脉敌人
        self.enemies[6] = Enemy(6, "兽人战士", EnemyType.ORC, 5, 100, 100, 18, 8, 50, 30,
                                "强壮的兽人族战士")
        self.enemies[7] = Enemy(7, "骷髅士兵", EnemyType.SKELETON, 4, 70, 70, 15, 5, 35, 20,
                                "被黑暗力量唤醒的骷髅")
        self.enemies[8] = Enemy(8, "巨魔", EnemyType.TROLL, 6, 150, 150, 22, 10, 70, 50,
                                "体型巨大但行动缓慢")

        # 诅咒沼泽敌人
        self.enemies[9] = Enemy(9, "剧毒史莱姆", EnemyType.SLIME, 7, 120, 120, 20, 6, 80, 60,
                                "带有剧毒的紫色史莱姆")
        self.enemies[10] = Enemy(10, "骷髅骑士", EnemyType.SKELETON, 8, 180, 180, 28, 15, 100, 80,
                                 "骑着骷髅马的强大骷髅")
        self.enemies[11] = Enemy(11, "邪恶法师", EnemyType.WIZARD, 9, 150, 150, 35, 8, 120, 100,
                                 "掌握黑暗魔法的法师")

        # 巨龙巢穴敌人
        self.enemies[12] = Enemy(12, "幼龙", EnemyType.DRAGON, 10, 300, 300, 40, 20, 200, 150,
                                 "尚未完全成长的龙")
        self.enemies[13] = Enemy(13, "火焰巨龙", EnemyType.DRAGON, 15, 500, 500, 60, 30, 500, 300,
                                 "掌控火焰的强大巨龙")

    def _initialize_quests(self):
        """初始化所有任务"""
        self.quests[1] = Quest(1, "清除哥布林",
                               "新手村附近的哥布林越来越多，请清除5只哥布林",
                               {"哥布林": 5}, 100, 50, [1])

        self.quests[2] = Quest(2, "收集野狼皮毛",
                               "裁缝需要3张野狼皮毛制作衣物",
                               {"野狼": 3}, 150, 80, [6])

        self.quests[3] = Quest(3, "消灭兽人",
                               "荒芜山脉的兽人部落威胁着村庄，消灭8只兽人",
                               {"兽人": 8}, 300, 150, [2, 9])

        self.quests[4] = Quest(4, "探索诅咒沼泽",
                               "探索诅咒沼泽并击败那里的首领",
                               {"邪恶法师": 1, "骷髅骑士": 3}, 500, 300, [7, 10])

        self.quests[5] = Quest(5, "屠龙勇士",
                               "击败火焰巨龙，成为传说中的屠龙勇士",
                               {"龙": 1}, 1000, 1000, [4, 8, 12])

    def _initialize_shops(self):
        """初始化商店"""
        # 新手村商店
        self.shops["新手村"] = {
            "name": "新手村商店",
            "items": [1, 2, 5, 6, 9, 10, 16, 17]
        }

        # 幽暗森林商店
        self.shops["幽暗森林"] = {
            "name": "森林交易所",
            "items": [2, 3, 6, 7, 10, 11, 17, 18]
        }

        # 荒芜山脉商店
        self.shops["荒芜山脉"] = {
            "name": "山麓市场",
            "items": [3, 4, 7, 8, 11, 12, 16, 17, 18]
        }

    def _initialize_regions(self):
        """初始化所有区域"""
        self.regions = {
            "新手村": {
                "name": "新手村",
                "description": "一个宁静的小村庄，冒险开始的地方",
                "enemies": [1, 2],
                "quests": [1, 2],
                "connections": ["幽暗森林"],
                "shop": True
            },
            "幽暗森林": {
                "name": "幽暗森林",
                "description": "茂密而阴暗的森林，隐藏着许多危险",
                "enemies": [3, 4, 5],
                "quests": [2, 3],
                "connections": ["新手村", "荒芜山脉"],
                "shop": True
            },
            "荒芜山脉": {
                "name": "荒芜山脉",
                "description": "贫瘠而危险的山脉地区",
                "enemies": [6, 7, 8],
                "quests": [3, 4],
                "connections": ["幽暗森林", "诅咒沼泽"],
                "shop": True
            },
            "诅咒沼泽": {
                "name": "诅咒沼泽",
                "description": "被黑暗力量腐蚀的沼泽地，充满危险",
                "enemies": [9, 10, 11],
                "quests": [4, 5],
                "connections": ["荒芜山脉", "巨龙巢穴"],
                "shop": False
            },
            "巨龙巢穴": {
                "name": "巨龙巢穴",
                "description": "巨龙居住的洞穴，终极挑战之地",
                "enemies": [12, 13],
                "quests": [5],
                "connections": ["诅咒沼泽"],
                "shop": False
            }
        }

    def get_region(self, region_name):
        """获取区域信息"""
        return self.regions.get(region_name)

    def get_random_enemy_for_region(self, region_name):
        """获取区域的随机敌人"""
        region = self.get_region(region_name)
        if not region or not region["enemies"]:
            return None

        enemy_id = random.choice(region["enemies"])
        base_enemy = self.enemies.get(enemy_id)

        if not base_enemy:
            return None

        # 创建敌人的副本，可以添加一些随机变异
        enemy = Enemy(
            id=base_enemy.id,
            name=base_enemy.name,
            enemy_type=base_enemy.enemy_type,
            level=base_enemy.level,
            health=base_enemy.max_health,
            max_health=base_enemy.max_health,
            attack=base_enemy.attack,
            defense=base_enemy.defense,
            xp_reward=base_enemy.xp_reward,
            gold_reward=base_enemy.gold_reward,
            description=base_enemy.description
        )

        # 随机化敌人的属性 (±20%)
        health_variation = random.randint(-3, 3)
        attack_variation = random.randint(-2, 2)

        enemy.health += health_variation
        enemy.max_health += health_variation
        enemy.attack += attack_variation

        return enemy

    def get_quests_for_region(self, region_name):
        """获取区域的任务"""
        region = self.get_region(region_name)
        if not region:
            return []

        quests = []
        for quest_id in region.get("quests", []):
            quest = self.quests.get(quest_id)
            if quest:
                quests.append(quest)

        return quests

    def get_shop_items(self, region_name):
        """获取商店物品"""
        shop_info = self.shops.get(region_name)
        if not shop_info:
            return []

        items = []
        for item_id in shop_info["items"]:
            item = self.items.get(item_id)
            if item:
                # 创建物品副本
                new_item = Item(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    item_type=item.item_type,
                    value=item.value,
                    price=item.price,
                    usable=item.usable
                )
                items.append(new_item)

        return items


# ==================== 游戏引擎类 ====================
class GameEngine:
    """游戏引擎类"""

    def __init__(self):
        self.world = GameWorld()
        self.player = None
        self.is_running = False
        self.current_battle = None

        # 游戏统计
        self.start_time = None
        self.total_battles = 0
        self.total_enemies_defeated = 0

    def start_game(self):
        """开始游戏"""
        self._show_title_screen()
        self._setup_player()
        self._game_loop()

    def _show_title_screen(self):
        """显示游戏标题"""
        os.system('cls' if os.name == 'nt' else 'clear')

        title = f"""
{GameConfig.Colors.CYAN}{'=' * 60}
{GameConfig.Colors.BOLD}{GameConfig.Colors.YELLOW}
   _____                    _         _____       _     _            
  |  __ \\                  | |       / ____|     | |   | |           
  | |  | | _____   _____ __| |______| (___   ___ | | __| | ___ _ __  
  | |  | |/ _ \\ \\ / / __/ _` |______|\\___ \\ / _ \\| |/ _` |/ _ \\ '_ \\ 
  | |__| | (_) \\ V / (_| (_| |       ____) | (_) | | (_| |  __/ | | |
  |_____/ \\___/ \\_/ \\___\\__,_|      |_____/ \\___/|_|\\__,_|\\___|_| |_|
{GameConfig.Colors.END}
{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}

              版本: {GameConfig.VERSION} | 作者: {GameConfig.AUTHOR}
"""
        print(title)

        print(f"{GameConfig.Colors.BOLD}游戏说明:{GameConfig.Colors.END}")
        print("1. 探索不同的区域，与敌人战斗")
        print("2. 完成任务获取奖励")
        print("3. 购买装备提升实力")
        print("4. 击败最终BOSS火焰巨龙")
        print()

        input("按回车键开始游戏...")

    def _setup_player(self):
        """设置玩家"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}创建角色{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        # 获取玩家名称
        while True:
            name = input("请输入你的角色名称: ").strip()
            if name:
                break
            print("名称不能为空！")

        # 选择难度
        print(f"\n{GameConfig.Colors.BOLD}选择难度:{GameConfig.Colors.END}")
        print("1. 简单 - 敌人较弱，获得经验更多")
        print("2. 普通 - 标准难度")
        print("3. 困难 - 敌人更强，获得经验更少")

        difficulty_choice = input("请选择难度 (1-3，默认2): ").strip()
        if difficulty_choice == "1":
            difficulty = "easy"
        elif difficulty_choice == "3":
            difficulty = "hard"
        else:
            difficulty = "normal"

        # 创建玩家
        self.player = Player(name, difficulty)
        self.start_time = time.time()

        print(f"\n{GameConfig.Colors.GREEN}角色创建成功！{GameConfig.Colors.END}")
        print(f"欢迎，{self.player.name}！")
        print(f"难度: {difficulty}")
        input("\n按回车键开始冒险...")

    def _game_loop(self):
        """游戏主循环"""
        self.is_running = True

        while self.is_running and self.player.health > 0:
            self._show_main_menu()

        # 游戏结束
        if self.player.health <= 0:
            self._game_over()
        else:
            self._game_complete()

    def _show_main_menu(self):
        """显示主菜单"""
        os.system('cls' if os.name == 'nt' else 'clear')

        # 显示玩家状态
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(self.player.get_status())
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        # 显示当前区域信息
        current_region = self.world.get_region(self.player.current_region)
        if current_region:
            print(f"\n{GameConfig.Colors.BOLD}当前区域: {current_region['name']}{GameConfig.Colors.END}")
            print(f"{current_region['description']}")

        # 显示主菜单选项
        print(f"\n{GameConfig.Colors.BOLD}主菜单:{GameConfig.Colors.END}")
        print("1. 探索当前区域")
        print("2. 移动到其他区域")
        print("3. 查看背包")
        print("4. 查看任务")
        print("5. 查看地图")
        print("6. 访问商店")
        print("7. 保存游戏")
        print("8. 加载游戏")
        print("9. 游戏统计")
        print("0. 退出游戏")

        choice = input(f"\n{GameConfig.Colors.BOLD}请选择操作 (0-9): {GameConfig.Colors.END}").strip()

        # 处理选择
        if choice == "1":
            self._explore_region()
        elif choice == "2":
            self._move_to_region()
        elif choice == "3":
            self._show_inventory()
        elif choice == "4":
            self._show_quests()
        elif choice == "5":
            self._show_map()
        elif choice == "6":
            self._visit_shop()
        elif choice == "7":
            self._save_game()
        elif choice == "8":
            self._load_game()
        elif choice == "9":
            self._show_stats()
        elif choice == "0":
            self._exit_game()
        else:
            print("无效的选择！")
            input("按回车键继续...")

    def _explore_region(self):
        """探索当前区域"""
        region_name = self.player.current_region

        # 随机事件
        event_chance = random.randint(1, 100)

        if event_chance <= 50:  # 50% 遇到敌人
            self._encounter_enemy()
        elif event_chance <= 75:  # 25% 发现物品
            self._find_item()
        elif event_chance <= 90:  # 15% 发现宝箱
            self._find_treasure()
        else:  # 10% 无事发生
            print("你探索了该区域，但没有发现什么特别的东西。")
            input("按回车键继续...")

    def _encounter_enemy(self):
        """遇到敌人"""
        enemy = self.world.get_random_enemy_for_region(self.player.current_region)

        if not enemy:
            print("该区域没有敌人。")
            input("按回车键继续...")
            return

        print(f"\n{GameConfig.Colors.RED}⚔️  遭遇敌人！{GameConfig.Colors.END}")
        print(f"{enemy.description}")
        print(f"你遇到了 {enemy}!")

        # 开始战斗
        self._start_battle(enemy)

    def _start_battle(self, enemy):
        """开始战斗"""
        print(f"\n{GameConfig.Colors.BOLD}战斗开始！{GameConfig.Colors.END}")

        battle_round = 1

        while enemy.is_alive() and self.player.health > 0:
            print(f"\n{GameConfig.Colors.CYAN}{'=' * 40}{GameConfig.Colors.END}")
            print(f"第 {battle_round} 回合")
            print(f"玩家: {self.player.health}/{self.player.max_health} HP")
            print(f"敌人: {enemy}")
            print(f"{GameConfig.Colors.CYAN}{'=' * 40}{GameConfig.Colors.END}")

            # 玩家行动
            print(f"\n{GameConfig.Colors.BOLD}选择行动:{GameConfig.Colors.END}")
            print("1. 攻击")
            print("2. 使用物品")
            print("3. 尝试逃跑")

            action = input("请选择行动 (1-3): ").strip()

            if action == "1":
                # 玩家攻击
                player_damage = self.player.attack + random.randint(-2, 3)
                actual_damage = enemy.take_damage(player_damage)
                print(f"你对{enemy.name}造成了{actual_damage}点伤害！")

                # 敌人反击（如果还活着）
                if enemy.is_alive():
                    enemy_damage = enemy.attack + random.randint(-2, 2)
                    actual_damage = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name}对你造成了{actual_damage}点伤害！")

            elif action == "2":
                # 使用物品
                self._use_item_in_battle()
                # 敌人仍然攻击
                if enemy.is_alive():
                    enemy_damage = enemy.attack + random.randint(-2, 2)
                    actual_damage = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name}对你造成了{actual_damage}点伤害！")

            elif action == "3":
                # 尝试逃跑
                escape_chance = 30 + (self.player.level * 5) - (enemy.level * 3)
                escape_chance = max(10, min(90, escape_chance))

                if random.randint(1, 100) <= escape_chance:
                    print(f"{GameConfig.Colors.GREEN}成功逃脱！{GameConfig.Colors.END}")
                    return
                else:
                    print(f"{GameConfig.Colors.RED}逃跑失败！{GameConfig.Colors.END}")
                    # 敌人攻击
                    enemy_damage = enemy.attack + random.randint(-2, 2)
                    actual_damage = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name}对你造成了{actual_damage}点伤害！")

            else:
                print("无效的行动，跳过本回合！")
                # 敌人攻击
                if enemy.is_alive():
                    enemy_damage = enemy.attack + random.randint(-2, 2)
                    actual_damage = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name}对你造成了{actual_damage}点伤害！")

            battle_round += 1

        # 战斗结束
        print(f"\n{GameConfig.Colors.CYAN}{'=' * 40}{GameConfig.Colors.END}")

        if enemy.is_alive():
            print(f"{GameConfig.Colors.RED}战斗失败！{GameConfig.Colors.END}")
            print(f"你被{enemy.name}击败了！")
        else:
            print(f"{GameConfig.Colors.GREEN}战斗胜利！{GameConfig.Colors.END}")
            print(f"你击败了{enemy.name}！")

            # 给予奖励
            xp_gained, levels_gained = self.player.add_xp(enemy.xp_reward)
            gold_gained = self.player.add_gold(enemy.gold_reward)

            print(f"获得 {xp_gained} 经验值")
            print(f"获得 {gold_gained} 金币")

            # 更新任务进度
            self.player.update_quest_progress(enemy.enemy_type)
            self.player.record_enemy_defeat(enemy.name)

            # 检查是否有任务完成
            self._check_quest_completion()

            # 更新统计
            self.total_battles += 1
            self.total_enemies_defeated += 1

        input("按回车键继续...")

    def _use_item_in_battle(self):
        """在战斗中使用物品"""
        # 获取可用的药水
        potions = [item for item in self.player.inventory if item.item_type == ItemType.POTION]

        if not potions:
            print("背包中没有可用的药水！")
            return

        print(f"\n{GameConfig.Colors.BOLD}可用的药水:{GameConfig.Colors.END}")
        for i, potion in enumerate(potions, 1):
            print(f"{i}. {potion.name} - 恢复{potion.value}点生命值")

        print(f"{len(potions) + 1}. 取消")

        try:
            choice = int(input("请选择药水: ").strip())
            if 1 <= choice <= len(potions):
                self.player.use_item(potions[choice - 1])
            else:
                print("取消使用物品")
        except (ValueError, IndexError):
            print("无效的选择！")

    def _find_item(self):
        """发现物品"""
        items_in_region = [
            item for item in self.world.items.values()
            if item.item_type in [ItemType.POTION, ItemType.MATERIAL, ItemType.TREASURE]
        ]

        if not items_in_region:
            print("该区域没有可发现的物品。")
            return

        found_item = random.choice(items_in_region)

        # 创建物品副本
        new_item = Item(
            id=found_item.id,
            name=found_item.name,
            description=found_item.description,
            item_type=found_item.item_type,
            value=found_item.value,
            price=found_item.price,
            usable=found_item.usable
        )

        print(f"\n{GameConfig.Colors.GREEN}✨ 你发现了一个物品！{GameConfig.Colors.END}")
        print(f"你找到了 {new_item.name}!")
        print(f"{new_item.description}")

        self.player.add_item(new_item)

        input("按回车键继续...")

    def _find_treasure(self):
        """发现宝箱"""
        treasure_items = [
            item for item in self.world.items.values()
            if item.item_type == ItemType.TREASURE
        ]

        if not treasure_items:
            print("该区域没有宝藏。")
            return

        found_treasure = random.choice(treasure_items)
        gold_found = random.randint(20, 100)

        print(f"\n{GameConfig.Colors.YELLOW}💰 你发现了一个宝箱！{GameConfig.Colors.END}")
        print("打开宝箱...")
        time.sleep(1)

        # 创建物品副本
        new_item = Item(
            id=found_treasure.id,
            name=found_treasure.name,
            description=found_treasure.description,
            item_type=found_treasure.item_type,
            value=found_treasure.value,
            price=found_treasure.price,
            usable=found_treasure.usable
        )

        print(f"你找到了 {new_item.name}!")
        print(f"还发现了 {gold_found} 金币!")

        self.player.add_item(new_item)
        self.player.add_gold(gold_found)

        input("按回车键继续...")

    def _move_to_region(self):
        """移动到其他区域"""
        current_region = self.world.get_region(self.player.current_region)

        if not current_region or not current_region.get("connections"):
            print("该区域没有可连接的其他区域。")
            input("按回车键继续...")
            return

        print(f"\n{GameConfig.Colors.BOLD}可移动的区域:{GameConfig.Colors.END}")
        connections = current_region["connections"]

        for i, region_name in enumerate(connections, 1):
            region_info = self.world.get_region(region_name)
            visited = "✓" if region_name in self.player.regions_visited else " "
            print(f"{i}. [{visited}] {region_name} - {region_info['description']}")

        print(f"{len(connections) + 1}. 取消移动")

        try:
            choice = int(input("请选择要移动到的区域: ").strip())
            if 1 <= choice <= len(connections):
                target_region = connections[choice - 1]
                self.player.move_to_region(target_region)

                # 恢复一些生命值（移动到新区域时）
                heal_amount = self.player.max_health // 10
                self.player.heal(heal_amount)

                print(f"\n{GameConfig.Colors.GREEN}你移动到了 {target_region}。{GameConfig.Colors.END}")
                print(f"移动过程中休息了一下，恢复了{heal_amount}点生命值。")
            else:
                print("取消移动")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")

    def _show_inventory(self):
        """显示背包"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}背包{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        # 显示装备
        print(f"\n{GameConfig.Colors.BOLD}当前装备:{GameConfig.Colors.END}")
        if self.player.weapon:
            print(f"武器: {self.player.weapon.name} (+{self.player.weapon.value}攻击)")
        else:
            print(f"武器: 无")

        if self.player.armor:
            print(f"护甲: {self.player.armor.name} (+{self.player.armor.value}防御)")
        else:
            print(f"护甲: 无")

        # 显示物品分类
        items_by_type = {}
        for item in self.player.inventory:
            item_type = item.item_type.value
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)

        if not items_by_type:
            print(f"\n{GameConfig.Colors.YELLOW}背包为空{GameConfig.Colors.END}")
        else:
            for item_type, items in items_by_type.items():
                print(f"\n{GameConfig.Colors.BOLD}{item_type}:{GameConfig.Colors.END}")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item}")

        # 显示操作菜单
        print(f"\n{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}操作:{GameConfig.Colors.END}")
        print("1. 使用物品")
        print("2. 装备物品")
        print("3. 卸下装备")
        print("4. 丢弃物品")
        print("0. 返回主菜单")

        choice = input(f"\n{GameConfig.Colors.BOLD}请选择操作 (0-4): {GameConfig.Colors.END}").strip()

        if choice == "1":
            self._use_item_from_inventory()
        elif choice == "2":
            self._equip_item_from_inventory()
        elif choice == "3":
            self._unequip_item()
        elif choice == "4":
            self._drop_item()
        elif choice == "0":
            return
        else:
            print("无效的选择！")
            input("按回车键继续...")
            self._show_inventory()

    def _use_item_from_inventory(self):
        """从背包使用物品"""
        usable_items = [item for item in self.player.inventory if item.usable]

        if not usable_items:
            print("没有可使用的物品！")
            input("按回车键继续...")
            self._show_inventory()
            return

        print(f"\n{GameConfig.Colors.BOLD}可使用的物品:{GameConfig.Colors.END}")
        for i, item in enumerate(usable_items, 1):
            if item.item_type == ItemType.POTION:
                print(f"{i}. {item.name} - 恢复{item.value}点生命值")
            else:
                print(f"{i}. {item.name}")

        print(f"{len(usable_items) + 1}. 取消")

        try:
            choice = int(input("请选择要使用的物品: ").strip())
            if 1 <= choice <= len(usable_items):
                self.player.use_item(usable_items[choice - 1])
            else:
                print("取消使用物品")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_inventory()

    def _equip_item_from_inventory(self):
        """从背包装备物品"""
        equippable_items = [
            item for item in self.player.inventory
            if item.item_type in [ItemType.WEAPON, ItemType.ARMOR]
        ]

        if not equippable_items:
            print("没有可装备的物品！")
            input("按回车键继续...")
            self._show_inventory()
            return

        print(f"\n{GameConfig.Colors.BOLD}可装备的物品:{GameConfig.Colors.END}")
        for i, item in enumerate(equippable_items, 1):
            stat_type = "攻击" if item.item_type == ItemType.WEAPON else "防御"
            print(f"{i}. {item.name} (+{item.value}{stat_type}) - {item.item_type.value}")

        print(f"{len(equippable_items) + 1}. 取消")

        try:
            choice = int(input("请选择要装备的物品: ").strip())
            if 1 <= choice <= len(equippable_items):
                item_to_equip = equippable_items[choice - 1]
                if self.player.equip_item(item_to_equip):
                    print(f"{GameConfig.Colors.GREEN}已装备 {item_to_equip.name}{GameConfig.Colors.END}")
                else:
                    print(f"{GameConfig.Colors.RED}无法装备该物品{GameConfig.Colors.END}")
            else:
                print("取消装备")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_inventory()

    def _unequip_item(self):
        """卸下装备"""
        if not self.player.weapon and not self.player.armor:
            print("没有装备任何物品！")
            input("按回车键继续...")
            self._show_inventory()
            return

        print(f"\n{GameConfig.Colors.BOLD}当前装备:{GameConfig.Colors.END}")
        options = []

        if self.player.weapon:
            print(f"1. 卸下武器: {self.player.weapon.name}")
            options.append("weapon")

        if self.player.armor:
            print(f"2. 卸下护甲: {self.player.armor.name}")
            options.append("armor")

        print(f"{len(options) + 1}. 取消")

        try:
            choice = int(input("请选择要卸下的装备: ").strip())
            if 1 <= choice <= len(options):
                item_type = options[choice - 1]
                if item_type == "weapon":
                    self.player.unequip_item(ItemType.WEAPON)
                    print(f"{GameConfig.Colors.GREEN}已卸下武器{GameConfig.Colors.END}")
                else:
                    self.player.unequip_item(ItemType.ARMOR)
                    print(f"{GameConfig.Colors.GREEN}已卸下护甲{GameConfig.Colors.END}")
            else:
                print("取消卸下")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_inventory()

    def _drop_item(self):
        """丢弃物品"""
        if not self.player.inventory:
            print("背包为空！")
            input("按回车键继续...")
            self._show_inventory()
            return

        print(f"\n{GameConfig.Colors.BOLD}背包物品:{GameConfig.Colors.END}")
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{i}. {item}")

        print(f"{len(self.player.inventory) + 1}. 取消")

        try:
            choice = int(input("请选择要丢弃的物品: ").strip())
            if 1 <= choice <= len(self.player.inventory):
                item_to_drop = self.player.inventory[choice - 1]

                # 如果是装备中的物品，先卸下
                if item_to_drop.equipped:
                    if item_to_drop.item_type == ItemType.WEAPON:
                        self.player.unequip_item(ItemType.WEAPON)
                    else:
                        self.player.unequip_item(ItemType.ARMOR)

                self.player.remove_item(item_to_drop)
                print(f"{GameConfig.Colors.YELLOW}已丢弃 {item_to_drop.name}{GameConfig.Colors.END}")
            else:
                print("取消丢弃")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_inventory()

    def _show_quests(self):
        """显示任务"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}任务日志{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        # 显示当前任务
        if self.player.quests:
            print(f"\n{GameConfig.Colors.BOLD}进行中的任务:{GameConfig.Colors.END}")
            for i, quest in enumerate(self.player.quests, 1):
                print(f"\n{i}. {quest}")
                for enemy_type, required in quest.requirements.items():
                    progress = quest.progress.get(enemy_type, 0)
                    print(f"   {enemy_type}: {progress}/{required}")
        else:
            print(f"\n{GameConfig.Colors.YELLOW}没有进行中的任务{GameConfig.Colors.END}")

        # 显示可接取的任务
        available_quests = self.world.get_quests_for_region(self.player.current_region)
        available_quests = [q for q in available_quests if q.status == QuestStatus.NOT_STARTED]

        if available_quests:
            print(f"\n{GameConfig.Colors.BOLD}可接取的任务:{GameConfig.Colors.END}")
            for i, quest in enumerate(available_quests, 1):
                print(f"\n{i}. {quest.name}")
                print(f"   {quest.description}")
                print(f"   奖励: {quest.reward_xp}经验, {quest.reward_gold}金币")

        # 显示已完成的任务
        if self.player.completed_quests:
            print(f"\n{GameConfig.Colors.BOLD}已完成的任务:{GameConfig.Colors.END}")
            for i, quest in enumerate(self.player.completed_quests, 1):
                print(f"{i}. {quest.name}")

        # 显示操作菜单
        print(f"\n{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}操作:{GameConfig.Colors.END}")
        print("1. 接受任务")
        print("2. 查看任务详情")
        print("0. 返回主菜单")

        choice = input(f"\n{GameConfig.Colors.BOLD}请选择操作 (0-2): {GameConfig.Colors.END}").strip()

        if choice == "1" and available_quests:
            self._accept_quest(available_quests)
        elif choice == "2" and (self.player.quests or self.player.completed_quests):
            self._view_quest_details()
        elif choice == "0":
            return
        else:
            print("无效的选择！")
            input("按回车键继续...")
            self._show_quests()

    def _accept_quest(self, available_quests):
        """接受任务"""
        print(f"\n{GameConfig.Colors.BOLD}可接受的任务:{GameConfig.Colors.END}")
        for i, quest in enumerate(available_quests, 1):
            print(f"{i}. {quest.name}")

        print(f"{len(available_quests) + 1}. 取消")

        try:
            choice = int(input("请选择要接受的任务: ").strip())
            if 1 <= choice <= len(available_quests):
                quest = available_quests[choice - 1]
                self.player.add_quest(quest)
                print(f"{GameConfig.Colors.GREEN}已接受任务: {quest.name}{GameConfig.Colors.END}")
            else:
                print("取消接受任务")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_quests()

    def _view_quest_details(self):
        """查看任务详情"""
        all_quests = self.player.quests + self.player.completed_quests

        if not all_quests:
            print("没有任务可查看！")
            input("按回车键继续...")
            self._show_quests()
            return

        print(f"\n{GameConfig.Colors.BOLD}所有任务:{GameConfig.Colors.END}")
        for i, quest in enumerate(all_quests, 1):
            status_symbol = "✓" if quest.status == QuestStatus.COMPLETED else "→"
            print(f"{i}. [{status_symbol}] {quest.name}")

        try:
            choice = int(input("请选择要查看的任务: ").strip())
            if 1 <= choice <= len(all_quests):
                quest = all_quests[choice - 1]

                print(f"\n{GameConfig.Colors.BOLD}任务详情:{GameConfig.Colors.END}")
                print(f"名称: {quest.name}")
                print(f"描述: {quest.description}")
                print(f"状态: {quest.status.value}")

                if quest.status == QuestStatus.IN_PROGRESS:
                    print(f"\n{GameConfig.Colors.BOLD}进度:{GameConfig.Colors.END}")
                    for enemy_type, required in quest.requirements.items():
                        progress = quest.progress.get(enemy_type, 0)
                        print(f"{enemy_type}: {progress}/{required}")

                print(f"\n{GameConfig.Colors.BOLD}奖励:{GameConfig.Colors.END}")
                print(f"经验值: {quest.reward_xp}")
                print(f"金币: {quest.reward_gold}")

                if quest.reward_items:
                    print("物品奖励:")
                    for item_id in quest.reward_items:
                        item = self.world.items.get(item_id)
                        if item:
                            print(f"  - {item.name}")
            else:
                print("取消查看")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._show_quests()

    def _check_quest_completion(self):
        """检查任务是否完成"""
        for quest in self.player.quests[:]:  # 使用副本遍历
            if quest.is_completed():
                self.player.complete_quest(quest)

    def _show_map(self):
        """显示地图"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}世界地图{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        # 显示所有区域
        for i, region_name in enumerate(GameConfig.REGIONS, 1):
            region_info = self.world.get_region(region_name)
            if not region_info:
                continue

            visited = "✓" if region_name in self.player.regions_visited else " "
            current = "★" if region_name == self.player.current_region else " "

            print(f"{i}. [{visited}{current}] {region_name}")
            print(f"   描述: {region_info['description']}")

            # 显示连接的区域
            if region_info.get("connections"):
                connections_str = "、".join(region_info["connections"])
                print(f"   连接: {connections_str}")

            # 显示区域等级
            if region_info.get("enemies"):
                min_level = min([self.world.enemies[eid].level for eid in region_info["enemies"]])
                max_level = max([self.world.enemies[eid].level for eid in region_info["enemies"]])
                print(f"   等级范围: Lv.{min_level}-{max_level}")

            print()

        input("按回车键返回主菜单...")

    def _visit_shop(self):
        """访问商店"""
        region_name = self.player.current_region
        shop_items = self.world.get_shop_items(region_name)

        if not shop_items:
            print("该区域没有商店。")
            input("按回车键继续...")
            return

        shop_name = self.world.shops.get(region_name, {}).get("name", "商店")

        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}{shop_name}{GameConfig.Colors.END}")
        print(f"金币: {self.player.gold}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        print(f"\n{GameConfig.Colors.BOLD}商品列表:{GameConfig.Colors.END}")
        for i, item in enumerate(shop_items, 1):
            print(f"{i}. {item.name} - {item.description}")
            print(f"   价格: {item.price}金币")
            print()

        # 显示操作菜单
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}操作:{GameConfig.Colors.END}")
        print("1. 购买商品")
        print("2. 出售物品")
        print("0. 离开商店")

        choice = input(f"\n{GameConfig.Colors.BOLD}请选择操作 (0-2): {GameConfig.Colors.END}").strip()

        if choice == "1":
            self._buy_item(shop_items)
        elif choice == "2":
            self._sell_item()
        elif choice == "0":
            return
        else:
            print("无效的选择！")
            input("按回车键继续...")
            self._visit_shop()

    def _buy_item(self, shop_items):
        """购买物品"""
        if not shop_items:
            print("商店没有商品！")
            input("按回车键继续...")
            self._visit_shop()
            return

        print(f"\n{GameConfig.Colors.BOLD}购买商品:{GameConfig.Colors.END}")
        for i, item in enumerate(shop_items, 1):
            print(f"{i}. {item.name} - {item.price}金币")

        print(f"{len(shop_items) + 1}. 取消")

        try:
            choice = int(input("请选择要购买的商品: ").strip())
            if 1 <= choice <= len(shop_items):
                item_to_buy = shop_items[choice - 1]

                if self.player.gold >= item_to_buy.price:
                    # 创建物品副本
                    new_item = Item(
                        id=item_to_buy.id,
                        name=item_to_buy.name,
                        description=item_to_buy.description,
                        item_type=item_to_buy.item_type,
                        value=item_to_buy.value,
                        price=item_to_buy.price,
                        usable=item_to_buy.usable
                    )

                    self.player.add_item(new_item)
                    self.player.gold -= item_to_buy.price

                    print(f"{GameConfig.Colors.GREEN}购买了 {new_item.name}！{GameConfig.Colors.END}")
                    print(f"剩余金币: {self.player.gold}")
                else:
                    print(
                        f"{GameConfig.Colors.RED}金币不足！需要{item_to_buy.price}金币，你只有{self.player.gold}金币。{GameConfig.Colors.END}")
            else:
                print("取消购买")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._visit_shop()

    def _sell_item(self):
        """出售物品"""
        if not self.player.inventory:
            print("背包为空，没有物品可出售！")
            input("按回车键继续...")
            self._visit_shop()
            return

        # 过滤掉任务物品
        sellable_items = [item for item in self.player.inventory if item.item_type != ItemType.QUEST]

        if not sellable_items:
            print("没有可出售的物品！")
            input("按回车键继续...")
            self._visit_shop()
            return

        print(f"\n{GameConfig.Colors.BOLD}可出售的物品:{GameConfig.Colors.END}")
        for i, item in enumerate(sellable_items, 1):
            sell_price = item.price // 2  # 出售价格为原价的一半
            print(f"{i}. {item.name} - {sell_price}金币")

        print(f"{len(sellable_items) + 1}. 取消")

        try:
            choice = int(input("请选择要出售的物品: ").strip())
            if 1 <= choice <= len(sellable_items):
                item_to_sell = sellable_items[choice - 1]
                sell_price = item_to_sell.price // 2

                # 如果是装备中的物品，先卸下
                if item_to_sell.equipped:
                    if item_to_sell.item_type == ItemType.WEAPON:
                        self.player.unequip_item(ItemType.WEAPON)
                    else:
                        self.player.unequip_item(ItemType.ARMOR)

                self.player.remove_item(item_to_sell)
                self.player.gold += sell_price

                print(
                    f"{GameConfig.Colors.YELLOW}出售了 {item_to_sell.name}，获得{sell_price}金币！{GameConfig.Colors.END}")
                print(f"剩余金币: {self.player.gold}")
            else:
                print("取消出售")
        except (ValueError, IndexError):
            print("无效的选择！")

        input("按回车键继续...")
        self._visit_shop()

    def _save_game(self):
        """保存游戏"""
        # 简化版保存功能
        print(f"{GameConfig.Colors.YELLOW}保存功能正在开发中...{GameConfig.Colors.END}")
        print("在完整版中，这里会将游戏数据保存到文件")
        input("按回车键继续...")

    def _load_game(self):
        """加载游戏"""
        # 简化版加载功能
        print(f"{GameConfig.Colors.YELLOW}加载功能正在开发中...{GameConfig.Colors.END}")
        print("在完整版中，这里会从文件加载游戏数据")
        input("按回车键继续...")

    def _show_stats(self):
        """显示游戏统计"""
        os.system('cls' if os.name == 'nt' else 'clear')

        # 计算游戏时间
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = "00:00:00"

        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.BOLD}游戏统计{GameConfig.Colors.END}")
        print(f"{GameConfig.Colors.CYAN}{'=' * 60}{GameConfig.Colors.END}")

        print(f"\n{GameConfig.Colors.BOLD}玩家信息:{GameConfig.Colors.END}")
        print(f"名称: {self.player.name}")
        print(f"等级: {self.player.level}")
        print(f"经验值: {self.player.xp}/{self.player.xp_to_next_level}")
        print(f"难度: {self.player.difficulty}")

        print(f"\n{GameConfig.Colors.BOLD}游戏进度:{GameConfig.Colors.END}")
        print(f"游戏时间: {time_str}")
        print(f"总战斗次数: {self.total_battles}")
        print(f"击败敌人总数: {self.total_enemies_defeated}")
        print(f"已探索区域: {len(self.player.regions_visited)}/{len(GameConfig.REGIONS)}")
        print(f"完成任务数: {len(self.player.completed_quests)}")

        print(f"\n{GameConfig.Colors.BOLD}击败的敌人:{GameConfig.Colors.END}")
        if self.player.enemies_defeated:
            for enemy_name, count in self.player.enemies_defeated.items():
                print(f"{enemy_name}: {count}次")
        else:
            print("暂无")

        # 击败巨龙的特殊统计
        if "火焰巨龙" in self.player.enemies_defeated:
            print(f"\n{GameConfig.Colors.YELLOW}★ 屠龙勇士成就已达成！{GameConfig.Colors.END}")

        input(f"\n按回车键返回主菜单...")

    def _exit_game(self):
        """退出游戏"""
        print(f"\n{GameConfig.Colors.YELLOW}确定要退出游戏吗？{GameConfig.Colors.END}")
        confirm = input("输入 'yes' 确认退出: ").strip().lower()

        if confirm in ['yes', 'y']:
            print(f"\n{GameConfig.Colors.GREEN}感谢游玩 {GameConfig.GAME_NAME}！{GameConfig.Colors.END}")
            self.is_running = False

    def _game_over(self):
        """游戏结束"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.RED}{'=' * 60}")
        print(f"""
   _____                         ____                 
  / ____|                       / __ \\                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \\ / _ \\ | |  | \\ \\ / / _ \\ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\\ V /  __/ |   
  \\_____|\\__,_|_| |_| |_|\\___|  \\____/  \\_/ \\___|_|   
        """)
        print(f"{'=' * 60}{GameConfig.Colors.END}")

        print(f"\n{GameConfig.Colors.BOLD}游戏结束，{self.player.name}！{GameConfig.Colors.END}")
        print(f"你坚持到了第 {self.player.level} 级")
        print(f"击败了 {self.total_enemies_defeated} 个敌人")
        print(f"完成了 {len(self.player.completed_quests)} 个任务")

        # 显示游戏时间
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"游戏时间: {minutes}分{seconds}秒")

        print(f"\n{GameConfig.Colors.YELLOW}希望下次你能走得更远！{GameConfig.Colors.END}")

        choice = input(f"\n{GameConfig.Colors.BOLD}重新开始游戏？(yes/no): {GameConfig.Colors.END}").strip().lower()
        if choice in ['yes', 'y']:
            self.__init__()
            self.start_game()
        else:
            print(f"\n{GameConfig.Colors.GREEN}感谢游玩 {GameConfig.GAME_NAME}！{GameConfig.Colors.END}")

    def _game_complete(self):
        """游戏通关"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"{GameConfig.Colors.YELLOW}{'=' * 60}")
        print(f"""
   _____                            _         _ 
  / ____|                          | |       | |
 | |     ___  _ __   __ _ _ __ __ _| |_ _   _| |
 | |    / _ \\| '_ \\ / _` | '__/ _` | __| | | | |
 | |___| (_) | | | | (_| | | | (_| | |_| |_| |_|
  \\_____\\___/|_| |_|\\__, |_|  \\__,_|\\__|\\__, (_)
                     __/ |               __/ |  
                    |___/               |___/   
        """)
        print(f"{'=' * 60}{GameConfig.Colors.END}")

        print(f"\n{GameConfig.Colors.BOLD}恭喜你，{self.player.name}！{GameConfig.Colors.END}")
        print(f"你成功击败了火焰巨龙，完成了 {GameConfig.GAME_NAME} 的冒险！")
        print(f"\n{GameConfig.Colors.CYAN}最终成绩:{GameConfig.Colors.END}")
        print(f"最终等级: {self.player.level}")
        print(f"总击败敌人: {self.total_enemies_defeated}")
        print(f"完成任务: {len(self.player.completed_quests)}/{len(self.world.quests)}")
        print(f"探索区域: {len(self.player.regions_visited)}/{len(GameConfig.REGIONS)}")

        # 显示游戏时间
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            print(f"总游戏时间: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # 评分
        score = (self.player.level * 100) + (self.total_enemies_defeated * 10) + (
                    len(self.player.completed_quests) * 200)
        print(f"\n{GameConfig.Colors.YELLOW}最终得分: {score}{GameConfig.Colors.END}")

        if score > 5000:
            print(f"{GameConfig.Colors.YELLOW}★★★★★ 传奇冒险家！{GameConfig.Colors.END}")
        elif score > 3000:
            print(f"{GameConfig.Colors.YELLOW}★★★★☆ 英勇的战士！{GameConfig.Colors.END}")
        else:
            print(f"{GameConfig.Colors.YELLOW}★★★☆☆ 合格的冒险者！{GameConfig.Colors.END}")

        choice = input(f"\n{GameConfig.Colors.BOLD}重新开始游戏？(yes/no): {GameConfig.Colors.END}").strip().lower()
        if choice in ['yes', 'y']:
            self.__init__()
            self.start_game()
        else:
            print(f"\n{GameConfig.Colors.GREEN}感谢游玩 {GameConfig.GAME_NAME}！{GameConfig.Colors.END}")


# ==================== 主程序入口 ====================
def main():
    """游戏主函数"""
    try:
        # 检查是否支持颜色输出
        if os.name == 'nt':  # Windows系统
            os.system('color')

        # 创建游戏引擎并启动游戏
        game = GameEngine()
        game.start_game()

    except KeyboardInterrupt:
        print(f"\n\n{GameConfig.Colors.YELLOW}游戏被中断{GameConfig.Colors.END}")
    except Exception as e:
        print(f"\n\n{GameConfig.Colors.RED}游戏发生错误: {e}{GameConfig.Colors.END}")
        import traceback
        traceback.print_exc()

        input("\n按回车键退出...")


if __name__ == "__main__":
    main()