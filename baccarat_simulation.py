import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 대신 Agg 백엔드 사용
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import numpy as np
import os
import glob

# 바카라 승률 설정 (실제 바카라 승률)
player_win_prob = 0.4462  # 플레이어 승률
banker_win_prob = 0.4586  # 뱅커 승률
tie_prob = 0.0952  # 타이 확률 (이 시뮬레이션에서는 무시)

# 초기 설정
initial_bet = 25  # 최소(기본) 베팅 금액을 25달러로 변경
initial_capital = 250  # 기본 자본 250달러

# 시뮬레이션 설정
rounds = 100  # 게임 횟수를 100판으로 변경
fps = 20      # 프레임 수 증가
interval = 50 # ms 단위로 더 부드럽게

a_total = initial_capital
b_total = initial_capital
a_bet = initial_bet
b_bet = initial_bet
a_direction = "Player"
b_direction = "Banker"

a_balance_history = [a_total]
b_balance_history = [b_total]
results = []

# 연승/연패 추적용
win_streak_a = [0]
lose_streak_a = [0]
current_win_a = 0
current_lose_a = 0

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스(-) 깨짐 방지

def can_bet(balance, bet):
    return balance >= bet

def safe_minmax(lst1, lst2):
    nums = [x for x in lst1 + lst2 if isinstance(x, (int, float)) and not (isinstance(x, float) and np.isnan(x))]
    if nums:
        y_min = min(nums) - 50
        y_max = max(nums) + 50
        if y_min == y_max:
            y_min -= 1
            y_max += 1
        return y_min, y_max
    else:
        return 0, 1

for rnd in range(rounds):
    # 둘 다 자본이 0 이하이면 게임 중단
    if a_total < initial_bet and b_total < initial_bet:
        break
    result = random.choices(["Player", "Banker"], weights=[player_win_prob, banker_win_prob])[0]
    win = (a_direction == result)

    # 각 플레이어가 베팅 가능한지 확인
    a_can_bet = a_total >= a_bet
    b_can_bet = b_total >= b_bet

    if a_can_bet and b_can_bet:
        if win:
            # A가 이긴 경우: 실제 베팅 가능한 금액만큼만 베팅
            actual_a_bet = min(a_total, a_bet)
            actual_b_bet = min(b_total, b_bet)
            a_total -= actual_a_bet
            a_total += actual_a_bet * 2  # 베팅 금액의 2배를 받음 (원금 + 상금)
            b_total -= actual_b_bet
            # 이긴 사람은 딴 만큼 다시 걸기 (이번에 딴 금액 = actual_a_bet)
            a_bet = min(a_total, actual_a_bet)
            b_bet = initial_bet
            a_direction = "Banker"
            b_direction = "Player"
            current_win_a += 1
            current_lose_a = 0
        else:
            # B가 이긴 경우: 실제 베팅 가능한 금액만큼만 베팅
            actual_a_bet = min(a_total, a_bet)
            actual_b_bet = min(b_total, b_bet)
            b_total -= actual_b_bet
            b_total += actual_b_bet * 2  # 베팅 금액의 2배를 받음 (원금 + 상금)
            a_total -= actual_a_bet
            # 이긴 사람은 딴 만큼 다시 걸기 (이번에 딴 금액 = actual_b_bet)
            b_bet = min(b_total, actual_b_bet)
            a_bet = initial_bet
            a_direction = "Player"
            b_direction = "Banker"
            current_lose_a += 1
            current_win_a = 0
    elif a_can_bet:
        # B는 파산, A만 베팅
        actual_a_bet = min(a_total, a_bet)
        a_total -= actual_a_bet
        a_total += actual_a_bet * 2
        a_bet = min(a_total, actual_a_bet)
        b_bet = initial_bet
    elif b_can_bet:
        # A는 파산, B만 베팅
        actual_b_bet = min(b_total, b_bet)
        b_total -= actual_b_bet
        b_total += actual_b_bet * 2
        b_bet = min(b_total, actual_b_bet)
        a_bet = initial_bet
    # 둘 다 못하면 아무것도 안 함

    # 자본이 0 이하로 떨어지면 0으로 고정
    a_total = max(a_total, 0)
    b_total = max(b_total, 0)

    a_balance_history.append(float(a_total))
    b_balance_history.append(float(b_total))
    results.append((a_total, b_total))
    win_streak_a.append(current_win_a)
    lose_streak_a.append(current_lose_a)

# gif 폴더가 없으면 생성
if not os.path.exists('gif'):
    os.makedirs('gif')

# 다음 파일 번호 찾기
existing_files = glob.glob('gif/*.gif')
if existing_files:
    numbers = []
    for file in existing_files:
        filename = os.path.basename(file)
        if filename.startswith('baccarat_') and filename.endswith('.gif'):
            try:
                num = int(filename.replace('baccarat_', '').replace('.gif', ''))
                numbers.append(num)
            except ValueError:
                continue
    next_number = max(numbers) + 1 if numbers else 1
else:
    next_number = 1

gif_filename = f'gif/baccarat_{next_number}.gif'
png_filename = f'gif/baccarat_{next_number}.png'

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, rounds)
# y축 범위 안전하게 지정
y_min, y_max = safe_minmax(a_balance_history, b_balance_history)
ax.set_ylim(y_min, y_max)
# 선 객체 생성 (마커 없이)
line_a, = ax.plot([], [], 'b-', label='A 자본', linewidth=2)
line_b, = ax.plot([], [], 'r-', label='B 자본', linewidth=2)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.set_title(f"A vs B 자본 흐름 애니메이션 ({rounds}판)", fontsize=14, fontweight='bold')
ax.set_xlabel("회차", fontsize=12)
ax.set_ylabel("자본 ($)", fontsize=12)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# 연승/연패에 따라 선 효과를 바꿔주는 함수
def set_line_effects(line, streak, base_color):
    # 연승이면 파란색 계열, 연패면 빨간색 계열, 기본은 base_color
    if streak > 1:
        # 연승: 선 두께 증가, 색 진해짐
        line.set_linewidth(2 + streak * 0.5)
        line.set_color((0, 0, min(1, 0.7 + 0.1 * streak)))  # 진한 파랑
    elif streak < -1:
        # 연패: 선 두께 증가, 색 빨강 계열
        line.set_linewidth(2 + abs(streak) * 0.5)
        line.set_color((min(1, 0.7 + 0.1 * abs(streak)), 0, 0))  # 진한 빨강
    else:
        line.set_linewidth(2)
        line.set_color(base_color)

# 애니메이션 초기화 함수
def init():
    line_a.set_data([], [])
    line_b.set_data([], [])
    return line_a, line_b

# 애니메이션 업데이트 함수
def update(frame):
    x = list(range(frame + 1))
    y_a = a_balance_history[:frame + 1]
    y_b = b_balance_history[:frame + 1]
    line_a.set_data(x, y_a)
    line_b.set_data(x, y_b)
    # 연승/연패 효과 적용 (A만 예시)
    streak = win_streak_a[frame] if win_streak_a[frame] > 0 else -lose_streak_a[frame]
    set_line_effects(line_a, streak, 'b')
    # B는 기본 스타일 유지
    line_b.set_linewidth(2)
    line_b.set_color('r')
    return line_a, line_b

ani = animation.FuncAnimation(
    fig, update, frames=rounds + 1, init_func=init,
    blit=True, interval=interval, repeat=False
)

plt.tight_layout()

print(f"애니메이션을 생성 중입니다...")
ani.save(gif_filename, writer='pillow', fps=fps)
print(f"애니메이션이 '{gif_filename}' 파일로 저장되었습니다!")

print(f"\n최종 결과:")
print(f"A의 최종 자본: ${a_total}")
print(f"B의 최종 자본: ${b_total}")
print(f"총 베팅 횟수: {rounds}회")

# 자본 그래프도 저장
plt.figure(figsize=(12, 6))
y_min, y_max = safe_minmax(a_balance_history, b_balance_history)
plt.ylim(y_min, y_max)
plt.plot(range(rounds + 1), a_balance_history, 'b-', label='A 자본', linewidth=2)
plt.plot(range(rounds + 1), b_balance_history, 'r-', label='B 자본', linewidth=2)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)

# 주요 구간마다 금액 라벨 표시 (20회차마다)
for i in range(0, rounds + 1, 20):
    plt.text(i, a_balance_history[i], f"{a_balance_history[i]:,}", color='blue', fontsize=8, ha='center', va='bottom', fontweight='bold')
    plt.text(i, b_balance_history[i], f"{b_balance_history[i]:,}", color='red', fontsize=8, ha='center', va='top', fontweight='bold')

# 마지막 금액을 크게 표시
plt.text(rounds, a_balance_history[-1], f"A: {a_balance_history[-1]:,}", color='blue', fontsize=18, ha='right', va='bottom', fontweight='bold', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
plt.text(rounds, b_balance_history[-1], f"B: {b_balance_history[-1]:,}", color='red', fontsize=18, ha='right', va='top', fontweight='bold', bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.5'))

# 그래프 제목에 최종 자본 명확히 표기
final_a = a_balance_history[-1]
final_b = b_balance_history[-1]

def capital_str(name, value):
    if value > 0:
        return f"{name}(자본): +{value:,}"
    elif value < 0:
        return f"{name}(손해): {value:,}"
    else:
        return f"{name}: 0"

if final_a > 0 and final_b > 0:
    result_str = f"{capital_str('A', final_a)}, {capital_str('B', final_b)}"
elif final_a < 0 and final_b < 0:
    result_str = f"{capital_str('A', final_a)}, {capital_str('B', final_b)}"
elif final_a == 0 and final_b == 0:
    result_str = f"A: 0, B: 0"
elif final_a != 0 and final_b == 0:
    result_str = capital_str('A', final_a)
elif final_b != 0 and final_a == 0:
    result_str = capital_str('B', final_b)
else:
    result_str = f"{capital_str('A', final_a)}, {capital_str('B', final_b)}"

plt.title(f"A vs B 자본 흐름 ({rounds}판) | 최종 자본 = {result_str}", fontsize=16, fontweight='bold')
plt.xlabel("회차", fontsize=12)
plt.ylabel("자본 ($)", fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(png_filename, dpi=300, bbox_inches='tight')
print(f"자본 그래프가 '{png_filename}' 파일로 저장되었습니다!") 