"""
北航自由搏击小游戏
基于pygame开发，以北航学习生活为背景的格斗游戏
作者：AI助手协助开发
"""

import pygame
import sys
import random
import math
import os
from enum import Enum

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)

def get_chinese_font(size):
    """获取支持中文的字体"""
    # Windows系统中文字体路径
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",   # 黑体
        "C:/Windows/Fonts/simsun.ttc",   # 宋体
        "C:/Windows/Fonts/simkai.ttf",   # 楷体
    ]
    
    # 尝试加载中文字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    # 如果系统字体都不可用，尝试使用pygame的默认字体
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.Font(pygame.font.get_default_font(), size)

class GameState(Enum):
    MENU = 1
    MODE_SELECT = 2
    DIFFICULTY_SELECT = 3
    PLAYING = 4
    GAME_OVER = 5
    PAUSE = 6

class GameMode(Enum):
    PVP = 1  # 玩家对玩家
    PVE = 2  # 玩家对AI

class AIDifficulty(Enum):
    EASY = 1    # 简单
    MEDIUM = 2  # 中等
    HARD = 3    # 困难
    EXPERT = 4  # 专家

class AIController:
    def __init__(self, fighter, difficulty):
        self.fighter = fighter
        self.difficulty = difficulty
        self.target = None
        self.last_decision_time = 0
        self.decision_interval = self._get_decision_interval()
        self.current_action = None
        self.action_timer = 0
        self.reaction_time = self._get_reaction_time()
        self.last_seen_player_x = 0
        
    def _get_decision_interval(self):
        """根据难度获取决策间隔"""
        intervals = {
            AIDifficulty.EASY: 1000,    # 1秒
            AIDifficulty.MEDIUM: 600,   # 0.6秒
            AIDifficulty.HARD: 300,     # 0.3秒
            AIDifficulty.EXPERT: 150    # 0.15秒
        }
        return intervals.get(self.difficulty, 600)
        
    def _get_reaction_time(self):
        """根据难度获取反应时间"""
        times = {
            AIDifficulty.EASY: 500,     # 0.5秒
            AIDifficulty.MEDIUM: 300,   # 0.3秒
            AIDifficulty.HARD: 150,     # 0.15秒
            AIDifficulty.EXPERT: 50     # 0.05秒
        }
        return times.get(self.difficulty, 300)
        
    def _get_skill_level(self):
        """根据难度获取技能等级参数"""
        skills = {
            AIDifficulty.EASY: {
                'accuracy': 0.3,        # 攻击精度
                'block_chance': 0.2,    # 防御概率
                'special_chance': 0.1,  # 特殊技能使用概率
                'combo_chance': 0.1,    # 连击概率
                'dodge_chance': 0.2,    # 闪避概率
                'dash_chance': 0.1      # 闪现概率
            },
            AIDifficulty.MEDIUM: {
                'accuracy': 0.5,
                'block_chance': 0.4,
                'special_chance': 0.3,
                'combo_chance': 0.3,
                'dodge_chance': 0.4,
                'dash_chance': 0.3
            },
            AIDifficulty.HARD: {
                'accuracy': 0.7,
                'block_chance': 0.6,
                'special_chance': 0.5,
                'combo_chance': 0.5,
                'dodge_chance': 0.6,
                'dash_chance': 0.5
            },
            AIDifficulty.EXPERT: {
                'accuracy': 0.9,
                'block_chance': 0.8,
                'special_chance': 0.7,
                'combo_chance': 0.7,
                'dodge_chance': 0.8,
                'dash_chance': 0.7
            }
        }
        return skills.get(self.difficulty, skills[AIDifficulty.MEDIUM])
        
    def update(self, target):
        self.target = target
        current_time = pygame.time.get_ticks()
        
        # 更新动作计时器
        if self.action_timer > 0:
            self.action_timer -= 1
            
        # 检查是否需要做出新决策
        if current_time - self.last_decision_time >= self.decision_interval:
            self._make_decision()
            self.last_decision_time = current_time
            
        # 执行当前动作
        return self._execute_action()
        
    def _make_decision(self):
        """AI决策逻辑"""
        if not self.target:
            return
            
        distance = abs(self.fighter.x - self.target.x)
        skill = self._get_skill_level()
        
        # 根据距离和情况选择动作
        if distance > 200:
            # 距离较远，接近目标或使用闪现
            if self.fighter.can_dash() and random.random() < skill['dash_chance']:
                self.current_action = 'dash'
                self.action_timer = 10
            elif self.target.x > self.fighter.x:
                self.current_action = 'move_right'
                self.action_timer = random.randint(30, 90)
            else:
                self.current_action = 'move_left'
                self.action_timer = random.randint(30, 90)
            
        elif distance > 80:
            # 中等距离，随机选择动作
            actions = ['move_closer', 'jump', 'wait']
            if random.random() < skill['special_chance'] and self.fighter.special_energy >= self.fighter.special_energy_cost:
                actions.append('special_attack')
            if self.fighter.can_dash() and random.random() < skill['dash_chance']:
                actions.append('dash')
            self.current_action = random.choice(actions)
            self.action_timer = random.randint(20, 60)
            
        else:
            # 近距离，战斗动作
            if self.target.is_attacking and random.random() < skill['block_chance']:
                self.current_action = 'block'
                self.action_timer = 20
            elif random.random() < skill['accuracy']:
                if random.random() < skill['special_chance'] and self.fighter.special_energy >= self.fighter.special_energy_cost:
                    self.current_action = 'special_attack'
                else:
                    self.current_action = 'attack'
                self.action_timer = 15
            elif random.random() < skill['dodge_chance']:
                # 闪避
                if self.fighter.can_dash() and random.random() < skill['dash_chance']:
                    self.current_action = 'dash'
                elif random.random() < 0.5:
                    self.current_action = 'jump'
                else:
                    self.current_action = 'move_back'
                self.action_timer = 30
            else:
                self.current_action = 'wait'
                self.action_timer = 10
                
    def _execute_action(self):
        """执行AI动作，返回模拟的按键状态"""
        if not self.current_action or self.action_timer <= 0:
            return {}
            
        # 创建虚拟按键状态
        virtual_keys = {}
        for key in self.fighter.controls.values():
            virtual_keys[key] = False
            
        if self.current_action == 'move_right':
            virtual_keys[self.fighter.controls['right']] = True
        elif self.current_action == 'move_left':
            virtual_keys[self.fighter.controls['left']] = True
        elif self.current_action == 'move_closer':
            if self.target.x > self.fighter.x:
                virtual_keys[self.fighter.controls['right']] = True
            else:
                virtual_keys[self.fighter.controls['left']] = True
        elif self.current_action == 'move_back':
            if self.target.x > self.fighter.x:
                virtual_keys[self.fighter.controls['left']] = True
            else:
                virtual_keys[self.fighter.controls['right']] = True
        elif self.current_action == 'jump':
            virtual_keys[self.fighter.controls['jump']] = True
        elif self.current_action == 'attack':
            virtual_keys[self.fighter.controls['attack']] = True
        elif self.current_action == 'special_attack':
            virtual_keys[self.fighter.controls['special']] = True
        elif self.current_action == 'block':
            virtual_keys[self.fighter.controls['block']] = True
        elif self.current_action == 'dash':
            virtual_keys[self.fighter.controls['dash']] = True
            
        return virtual_keys

class Fighter:
    def __init__(self, x, y, name, color, controls):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.name = name
        self.color = color
        self.health = 100
        self.max_health = 100
        self.speed = 5
        self.jump_power = 15
        self.velocity_y = 0
        self.on_ground = True
        self.facing_right = True
        self.controls = controls
        
        # 战斗属性
        self.attack_power = 10
        self.defense = 5
        self.combo_count = 0
        self.last_attack_time = 0
        self.attack_cooldown = 300  # 毫秒
        self.is_attacking = False
        self.attack_animation_time = 0
        
        # 特殊技能 - 降低能量消耗
        self.special_energy = 0
        self.max_special_energy = 100
        self.special_energy_cost = 25  # 从50降低到25
        self.is_blocking = False
        
        # 闪现功能
        self.dash_distance = 100  # 闪现距离
        self.dash_cooldown = 3000  # 3秒冷却时间
        self.last_dash_time = 0
        self.is_dashing = False
        self.dash_animation_time = 0
        
        # 动画状态
        self.animation_frame = 0
        self.animation_timer = 0
        
        # 状态效果
        self.stunned = False
        self.stun_timer = 0
        
    def update(self, keys, ground_y):
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            return
            
        # 闪现动画更新
        if self.is_dashing:
            self.dash_animation_time -= 1
            if self.dash_animation_time <= 0:
                self.is_dashing = False
            
        # 移动控制
        if keys[self.controls['left']] and not self.is_attacking and not self.is_dashing:
            self.x -= self.speed
            self.facing_right = False
            if self.x < 0:
                self.x = 0
                
        if keys[self.controls['right']] and not self.is_attacking and not self.is_dashing:
            self.x += self.speed
            self.facing_right = True
            if self.x > SCREEN_WIDTH - self.width:
                self.x = SCREEN_WIDTH - self.width
                
        # 跳跃控制
        if keys[self.controls['jump']] and self.on_ground and not self.is_attacking and not self.is_dashing:
            self.velocity_y = -self.jump_power
            self.on_ground = False
            
        # 防御控制
        self.is_blocking = keys[self.controls['block']] and not self.is_dashing
        
        # 重力和落地检测
        if not self.on_ground:
            self.velocity_y += 0.8  # 重力
            self.y += self.velocity_y
            
            if self.y >= ground_y - self.height:
                self.y = ground_y - self.height
                self.velocity_y = 0
                self.on_ground = True
                
        # 攻击动画更新
        if self.is_attacking:
            self.attack_animation_time -= 1
            if self.attack_animation_time <= 0:
                self.is_attacking = False
                
        # 动画更新
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
            
    def attack(self, target):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
            
        if self.is_attacking or self.stunned or self.is_dashing:
            return False
            
        # 检查攻击范围
        attack_range = 80
        distance = abs(self.x - target.x)
        
        if distance <= attack_range:
            self.is_attacking = True
            self.attack_animation_time = 15
            self.last_attack_time = current_time
            
            # 计算伤害
            damage = self.attack_power
            if target.is_blocking:
                damage = max(1, damage // 2)  # 防御减半伤害
            else:
                # 连击加成
                if current_time - self.last_attack_time < 1000:
                    self.combo_count += 1
                    damage += self.combo_count * 2
                else:
                    self.combo_count = 0
                    
            target.take_damage(damage)
            
            # 增加特殊能量 - 提高能量获得
            self.special_energy = min(self.max_special_energy, self.special_energy + 15)  # 从10提高到15
            
            return True
        return False
        
    def special_attack(self, target):
        if self.special_energy < self.special_energy_cost or self.stunned or self.is_dashing:
            return False
            
        # 检查特殊攻击范围
        special_range = 120
        distance = abs(self.x - target.x)
        
        if distance <= special_range:
            self.special_energy -= self.special_energy_cost  # 使用新的能量消耗
            self.is_attacking = True
            self.attack_animation_time = 30
            
            # 特殊攻击造成更大伤害和击晕效果
            damage = self.attack_power * 2
            if not target.is_blocking:
                target.stunned = True
                target.stun_timer = 60
                
            target.take_damage(damage)
            return True
        return False
        
    def dash(self):
        """闪现功能"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time < self.dash_cooldown:
            return False
            
        if self.stunned or self.is_attacking or self.is_dashing:
            return False
            
        # 执行闪现
        self.last_dash_time = current_time
        self.is_dashing = True
        self.dash_animation_time = 10  # 闪现动画持续时间
        
        # 根据面向方向闪现
        if self.facing_right:
            self.x += self.dash_distance
            if self.x > SCREEN_WIDTH - self.width:
                self.x = SCREEN_WIDTH - self.width
        else:
            self.x -= self.dash_distance
            if self.x < 0:
                self.x = 0
                
        return True
        
    def can_dash(self):
        """检查是否可以闪现"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_dash_time >= self.dash_cooldown and not self.stunned and not self.is_attacking and not self.is_dashing
        
    def get_dash_cooldown_remaining(self):
        """获取闪现剩余冷却时间"""
        current_time = pygame.time.get_ticks()
        remaining = self.dash_cooldown - (current_time - self.last_dash_time)
        return max(0, remaining) / 1000  # 转换为秒
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0
            
    def draw(self, screen):
        # 绘制角色主体
        color = self.color
        if self.stunned:
            color = YELLOW  # 击晕状态用黄色显示
        elif self.is_blocking:
            color = BLUE  # 防御状态用蓝色显示
        elif self.is_attacking:
            color = RED   # 攻击状态用红色显示
        elif self.is_dashing:
            color = WHITE  # 闪现状态用白色显示
            
        # 闪现时添加透明效果
        if self.is_dashing:
            # 创建半透明表面
            dash_surface = pygame.Surface((self.width, self.height))
            dash_surface.set_alpha(150)  # 半透明
            dash_surface.fill(color)
            screen.blit(dash_surface, (self.x, self.y))
        else:
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # 绘制眼睛
        eye_size = 5
        if self.facing_right:
            eye_x = self.x + self.width - 15
        else:
            eye_x = self.x + 10
        pygame.draw.circle(screen, WHITE, (eye_x, self.y + 15), eye_size)
        pygame.draw.circle(screen, BLACK, (eye_x, self.y + 15), eye_size - 2)
        
        # 绘制手臂（攻击时延伸）
        arm_length = 20
        if self.is_attacking:
            arm_length = 40
            
        if self.facing_right:
            arm_end_x = self.x + self.width + arm_length
        else:
            arm_end_x = self.x - arm_length
            
        pygame.draw.line(screen, color, 
                        (self.x + self.width//2, self.y + 30), 
                        (arm_end_x, self.y + 30), 5)
        
        # 绘制腿部
        leg_y = self.y + self.height
        pygame.draw.line(screen, color,
                        (self.x + 15, leg_y),
                        (self.x + 15, leg_y + 10), 8)
        pygame.draw.line(screen, color,
                        (self.x + self.width - 15, leg_y),
                        (self.x + self.width - 15, leg_y + 10), 8)
        
        # 绘制名字（使用中文字体）
        font = get_chinese_font(24)
        name_text = font.render(self.name, True, WHITE)
        screen.blit(name_text, (self.x, self.y - 25))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("北航自由搏击大赛")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        
        # 使用中文字体
        self.font_large = get_chinese_font(48)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(24)
        
        # 游戏模式和AI设置
        self.game_mode = GameMode.PVP
        self.ai_difficulty = AIDifficulty.MEDIUM
        self.ai_controller = None
        
        # 地面高度
        self.ground_y = SCREEN_HEIGHT - 100
        
        # 创建战斗角色
        self.create_fighters()
        
        # 游戏状态
        self.game_time = 180  # 3分钟倒计时
        self.winner = None
        self.round_count = 1
        self.max_rounds = 3
        
        # 背景元素
        self.background_elements = self.create_background()
        
        # 菜单选择
        self.menu_selection = 0
        self.mode_selection = 0
        self.difficulty_selection = 0
        
    def create_fighters(self):
        # 玩家1控制键位
        p1_controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_w,
            'attack': pygame.K_f,
            'block': pygame.K_s,
            'special': pygame.K_g,
            'dash': pygame.K_SPACE  # 添加闪现键位
        }
        
        # 玩家2/AI控制键位
        p2_controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_UP,
            'attack': pygame.K_PERIOD,
            'block': pygame.K_DOWN,
            'special': pygame.K_SLASH,
            'dash': pygame.K_RSHIFT  # 添加闪现键位
        }
        
        self.player1 = Fighter(200, self.ground_y - 80, "北航学霸", GREEN, p1_controls)
        if self.game_mode == GameMode.PVE:
            self.player2 = Fighter(600, self.ground_y - 80, "AI导师", ORANGE, p2_controls)
            self.ai_controller = AIController(self.player2, self.ai_difficulty)
        else:
            self.player2 = Fighter(600, self.ground_y - 80, "计算机系大神", PURPLE, p2_controls)
            self.ai_controller = None
        
    def create_background(self):
        elements = []
        # 创建一些装饰性背景元素（代表北航建筑）
        for i in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(50, 200)
            width = random.randint(40, 80)
            height = random.randint(60, 120)
            elements.append({'x': x, 'y': y, 'width': width, 'height': height})
        return elements
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % 3
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.menu_selection == 0:  # 人机对战
                            self.game_mode = GameMode.PVE
                            self.state = GameState.DIFFICULTY_SELECT
                        elif self.menu_selection == 1:  # 双人对战
                            self.game_mode = GameMode.PVP
                            self.state = GameState.PLAYING
                            self.create_fighters()
                            self.reset_game()
                        elif self.menu_selection == 2:  # 退出游戏
                            return False
                            
                elif self.state == GameState.DIFFICULTY_SELECT:
                    if event.key == pygame.K_UP:
                        self.difficulty_selection = (self.difficulty_selection - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.difficulty_selection = (self.difficulty_selection + 1) % 4
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        difficulties = [AIDifficulty.EASY, AIDifficulty.MEDIUM, AIDifficulty.HARD, AIDifficulty.EXPERT]
                        self.ai_difficulty = difficulties[self.difficulty_selection]
                        self.state = GameState.PLAYING
                        self.create_fighters()
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                        
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSE
                    elif event.key == self.player1.controls['attack']:
                        self.player1.attack(self.player2)
                    elif event.key == self.player1.controls['special']:
                        self.player1.special_attack(self.player2)
                    elif event.key == self.player1.controls['dash']:
                        self.player1.dash()
                    # 只有在PVP模式下才处理玩家2的输入
                    elif self.game_mode == GameMode.PVP:
                        if event.key == self.player2.controls['attack']:
                            self.player2.attack(self.player1)
                        elif event.key == self.player2.controls['special']:
                            self.player2.special_attack(self.player1)
                        elif event.key == self.player2.controls['dash']:
                            self.player2.dash()
                            
                elif self.state == GameState.PAUSE:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU
                        
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.MENU
                        
        return True
        
    def update(self):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            
            # 更新玩家1
            self.player1.update(keys, self.ground_y)
            
            # 更新玩家2或AI
            if self.game_mode == GameMode.PVE and self.ai_controller:
                # AI控制玩家2
                ai_keys = self.ai_controller.update(self.player1)
                
                # 创建一个可以处理AI虚拟按键的键状态对象
                class CombinedKeys:
                    def __init__(self, real_keys, virtual_keys):
                        self.real_keys = real_keys
                        self.virtual_keys = virtual_keys
                    
                    def __getitem__(self, key):
                        # 首先检查虚拟按键
                        if key in self.virtual_keys:
                            return self.virtual_keys[key]
                        # 然后检查真实按键，确保索引在范围内
                        if key < len(self.real_keys):
                            return self.real_keys[key]
                        return False
                
                combined_keys = CombinedKeys(keys, ai_keys)
                self.player2.update(combined_keys, self.ground_y)
                
                # AI执行攻击和闪现
                if ai_keys.get(self.player2.controls['attack'], False):
                    self.player2.attack(self.player1)
                elif ai_keys.get(self.player2.controls['special'], False):
                    self.player2.special_attack(self.player1)
                elif ai_keys.get(self.player2.controls['dash'], False):
                    self.player2.dash()
            else:
                # 玩家控制玩家2
                self.player2.update(keys, self.ground_y)
            
            # 更新游戏时间
            self.game_time -= 1/FPS
            
            # 检查游戏结束条件
            if self.player1.health <= 0:
                self.winner = self.player2
                self.state = GameState.GAME_OVER
            elif self.player2.health <= 0:
                self.winner = self.player1
                self.state = GameState.GAME_OVER
            elif self.game_time <= 0:
                # 时间结束，血量多的获胜
                if self.player1.health > self.player2.health:
                    self.winner = self.player1
                elif self.player2.health > self.player1.health:
                    self.winner = self.player2
                else:
                    self.winner = None  # 平局
                self.state = GameState.GAME_OVER
                
    def reset_game(self):
        self.player1.health = self.player1.max_health
        self.player2.health = self.player2.max_health
        self.player1.special_energy = 0
        self.player2.special_energy = 0
        self.player1.x = 200
        self.player2.x = 600
        self.player1.y = self.ground_y - 80
        self.player2.y = self.ground_y - 80
        self.game_time = 180
        self.winner = None
        
    def draw_ui(self):
        # 绘制血条
        bar_width = 300
        bar_height = 20
        
        # 玩家1血条
        p1_health_ratio = self.player1.health / self.player1.max_health
        pygame.draw.rect(self.screen, RED, (50, 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (50, 50, bar_width * p1_health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (50, 50, bar_width, bar_height), 2)
        
        # 玩家2血条
        p2_health_ratio = self.player2.health / self.player2.max_health
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 350, 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 350, 50, bar_width * p2_health_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 350, 50, bar_width, bar_height), 2)
        
        # 绘制特殊能量条
        special_bar_height = 10
        
        # 玩家1特殊能量
        p1_special_ratio = self.player1.special_energy / self.player1.max_special_energy
        pygame.draw.rect(self.screen, BLUE, (50, 80, bar_width * p1_special_ratio, special_bar_height))
        pygame.draw.rect(self.screen, WHITE, (50, 80, bar_width, special_bar_height), 1)
        
        # 玩家2特殊能量
        p2_special_ratio = self.player2.special_energy / self.player2.max_special_energy
        pygame.draw.rect(self.screen, BLUE, (SCREEN_WIDTH - 350, 80, bar_width * p2_special_ratio, special_bar_height))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 350, 80, bar_width, special_bar_height), 1)
        
        # 绘制闪现冷却指示器
        dash_bar_height = 8
        
        # 玩家1闪现冷却
        p1_dash_remaining = self.player1.get_dash_cooldown_remaining()
        if p1_dash_remaining > 0:
            p1_dash_ratio = 1 - (p1_dash_remaining / 3.0)  # 3秒冷却
            pygame.draw.rect(self.screen, ORANGE, (50, 95, bar_width * p1_dash_ratio, dash_bar_height))
            pygame.draw.rect(self.screen, WHITE, (50, 95, bar_width, dash_bar_height), 1)
        else:
            pygame.draw.rect(self.screen, GREEN, (50, 95, bar_width, dash_bar_height))
            pygame.draw.rect(self.screen, WHITE, (50, 95, bar_width, dash_bar_height), 1)
        
        # 玩家2闪现冷却
        p2_dash_remaining = self.player2.get_dash_cooldown_remaining()
        if p2_dash_remaining > 0:
            p2_dash_ratio = 1 - (p2_dash_remaining / 3.0)  # 3秒冷却
            pygame.draw.rect(self.screen, ORANGE, (SCREEN_WIDTH - 350, 95, bar_width * p2_dash_ratio, dash_bar_height))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 350, 95, bar_width, dash_bar_height), 1)
        else:
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 350, 95, bar_width, dash_bar_height))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 350, 95, bar_width, dash_bar_height), 1)
        
        # 绘制时间
        time_text = self.font_medium.render(f"时间: {int(self.game_time)}", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(time_text, time_rect)
        
        # 绘制连击数
        if self.player1.combo_count > 0:
            combo_text = self.font_small.render(f"连击: {self.player1.combo_count}", True, YELLOW)
            self.screen.blit(combo_text, (50, 110))
            
        if self.player2.combo_count > 0:
            combo_text = self.font_small.render(f"连击: {self.player2.combo_count}", True, YELLOW)
            self.screen.blit(combo_text, (SCREEN_WIDTH - 150, 110))
            
        # 绘制控制说明
        control_y = SCREEN_HEIGHT - 80
        if self.game_mode == GameMode.PVP:
            # 双人对战控制说明
            p1_controls = self.font_small.render("玩家1: WASD移动 F攻击 S防御 G特技 空格闪现", True, WHITE)
            p2_controls = self.font_small.render("玩家2: 方向键移动 .攻击 ↓防御 /特技 右Shift闪现", True, WHITE)
            self.screen.blit(p1_controls, (20, control_y))
            self.screen.blit(p2_controls, (20, control_y + 25))
        else:
            # 人机对战控制说明
            player_controls = self.font_small.render("控制: WASD移动 F攻击 S防御 G特技 空格闪现 ESC暂停", True, WHITE)
            self.screen.blit(player_controls, (20, control_y))
            
        # 绘制UI说明
        ui_hint1 = self.font_small.render("蓝色条: 特技能量(25%即可释放) 橙/绿条: 闪现冷却", True, YELLOW)
        ui_hint2 = self.font_small.render("特技能量消耗降低，闪现CD3秒，攻击更频繁", True, YELLOW)
        self.screen.blit(ui_hint1, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 50))
        self.screen.blit(ui_hint2, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT - 25))
        
    def draw(self):
        self.screen.fill(LIGHT_BLUE)  # 天空色背景
        
        # 绘制背景建筑
        for element in self.background_elements:
            pygame.draw.rect(self.screen, GRAY, 
                           (element['x'], element['y'], element['width'], element['height']))
            # 窗户
            for i in range(2):
                for j in range(3):
                    window_x = element['x'] + 10 + i * 20
                    window_y = element['y'] + 10 + j * 25
                    if window_x < element['x'] + element['width'] - 10 and window_y < element['y'] + element['height'] - 10:
                        pygame.draw.rect(self.screen, YELLOW, (window_x, window_y, 8, 12))
        
        # 绘制地面
        pygame.draw.rect(self.screen, GREEN, (0, self.ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.ground_y))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state == GameState.PLAYING:
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.draw_ui()
        elif self.state == GameState.PAUSE:
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            self.draw_ui()
            self.draw_pause()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
            
    def draw_menu(self):
        title_text = self.font_large.render("北航自由搏击大赛", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_medium.render("AI+X 创意作品", True, BLACK)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 菜单选项
        menu_options = ["人机对战", "双人对战", "退出游戏"]
        for i, option in enumerate(menu_options):
            color = RED if i == self.menu_selection else BLACK
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20 + i * 50))
            self.screen.blit(option_text, option_rect)
            
        # 控制说明
        instruction_text = self.font_small.render("使用↑↓键选择，回车确认", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(instruction_text, instruction_rect)
        
    def draw_difficulty_select(self):
        title_text = self.font_large.render("选择AI难度", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        self.screen.blit(title_text, title_rect)
        
        # 难度选项
        difficulty_options = [
            ("简单", "AI反应较慢，攻击精度低"),
            ("中等", "AI有一定战术，适中难度"),
            ("困难", "AI反应迅速，攻击精准"),
            ("专家", "AI大师级别，极具挑战性")
        ]
        
        for i, (name, desc) in enumerate(difficulty_options):
            color = RED if i == self.difficulty_selection else BLACK
            name_text = self.font_medium.render(name, True, color)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80 + i * 60))
            self.screen.blit(name_text, name_rect)
            
            desc_color = GRAY if i == self.difficulty_selection else BLACK
            desc_text = self.font_small.render(desc, True, desc_color)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50 + i * 60))
            self.screen.blit(desc_text, desc_rect)
            
        # 控制说明
        instruction_text = self.font_small.render("使用↑↓键选择难度，回车确认，ESC返回", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200))
        self.screen.blit(instruction_text, instruction_rect)
            
    def draw_pause(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("游戏暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font_medium.render("按ESC继续, 按Q返回主菜单", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(resume_text, resume_rect)
        
    def draw_game_over(self):
        if self.winner:
            winner_text = self.font_large.render(f"{self.winner.name} 获胜!", True, BLACK)
        else:
            winner_text = self.font_large.render("平局!", True, BLACK)
            
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(winner_text, winner_rect)
        
        restart_text = self.font_medium.render("按空格键返回主菜单", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()