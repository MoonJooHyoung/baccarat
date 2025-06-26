import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random
import os
import glob

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 피보나치 수열 (초기 구간)
fibo_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

# 시뮬레이션 변수 초기화
n_rounds = 100
unit_bet = 25  # 25달러 단위 베팅으로 변경

# 각 플레이어 상태
players = {
    'A': {'index':0, 'capital': 250, 'history': [], 'bet_history': []},
    'B': {'index':0, 'capital': 250, 'history': [], 'bet_history': []},
}

# 뱅커 승률과 수수료
banker_win_prob = 0.4586
commission = 0.05

def play_round(player):
    # 현재 베팅 금액
    bet_units = fibo_seq[player['index']]
    bet_amount = bet_units * unit_bet

    # 베팅 금액이 자본보다 크면 베팅 가능한 최대치로 조정
    if bet_amount > player['capital']:
        bet_amount = player['capital']
        # 배팅 단위에 맞게 index 조정 (가장 작은 피보나치 수 이하로 내림)
        for i, val in enumerate(fibo_seq):
            if val * unit_bet >= bet_amount:
                player['index'] = i
                break
    # 자본이 0 이하이면 베팅 중단
    if player['capital'] <= 0:
        player['history'].append(player['capital'])
        player['bet_history'].append(0)
        return
    # 결과 결정 (뱅커 승리 확률 적용)
    win = random.random() < banker_win_prob
    # 배팅 결과 반영
    if win:
        gain = bet_amount * 0.95
        player['capital'] += gain
        player['index'] = max(player['index'] - 2, 0)
    else:
        player['capital'] -= bet_amount
        player['index'] = min(player['index'] + 1, len(fibo_seq) - 1)
    player['history'].append(player['capital'])
    player['bet_history'].append(bet_amount)

# 100판 시뮬레이션 데이터 생성
for _ in range(n_rounds):
    # 둘 다 자본이 0 이하이면 전체 게임 중단
    if players['A']['capital'] <= 0 and players['B']['capital'] <= 0:
        break
    for p in players.values():
        play_round(p)

# gif 폴더가 없으면 생성
if not os.path.exists('gif'):
    os.makedirs('gif')

# 다음 파일 번호 찾기
existing_files = glob.glob('gif/fibonacci_*.gif')
if existing_files:
    numbers = []
    for file in existing_files:
        filename = os.path.basename(file)
        if filename.startswith('fibonacci_') and filename.endswith('.gif'):
            try:
                num = int(filename.replace('fibonacci_', '').replace('.gif', ''))
                numbers.append(num)
            except ValueError:
                continue
    next_number = max(numbers) + 1 if numbers else 1
else:
    next_number = 1

gif_filename = f'gif/fibonacci_{next_number}.gif'
png_filename = f'gif/fibonacci_{next_number}.png'

# 애니메이션 그리기
fig, ax = plt.subplots(figsize=(12,6))
ax.set_xlim(0, n_rounds)
min_capital = min(min(p['history']) for p in players.values())
max_capital = max(max(p['history']) for p in players.values())
ax.set_ylim(min_capital*0.95, max_capital*1.05)
ax.set_xlabel('판 수')
ax.set_ylabel('자본 ($)')

line_A, = ax.plot([], [], 'b-', label='Player A', linewidth=2)
line_B, = ax.plot([], [], 'r-', label='Player B', linewidth=2)
ax.legend(fontsize=10)

# 마지막 자본을 크게 표시
final_a = players['A']['history'][-1]
final_b = players['B']['history'][-1]
def profit_str(name, value):
    if value > 0:
        return f"{name}(수익): +{value:,.0f}"
    elif value < 0:
        return f"{name}(손해): {value:,.0f}"
    else:
        return f"{name}: 0"
if final_a > 0 and final_b > 0:
    result_str = f"{profit_str('A', final_a)}, {profit_str('B', final_b)}"
elif final_a < 0 and final_b < 0:
    result_str = f"{profit_str('A', final_a)}, {profit_str('B', final_b)}"
elif final_a == 0 and final_b == 0:
    result_str = f"A: 0, B: 0"
elif final_a != 0 and final_b == 0:
    result_str = profit_str('A', final_a)
elif final_b != 0 and final_a == 0:
    result_str = profit_str('B', final_b)
else:
    result_str = f"{profit_str('A', final_a)}, {profit_str('B', final_b)}"

plt.title(f"피보나치 배팅법 100판 자본 변화 | 최종 수익 = {result_str}", fontsize=16, fontweight='bold')
plt.text(n_rounds, final_a, f"A: {final_a:,.0f}", color='blue', fontsize=18, ha='right', va='bottom', fontweight='bold', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
plt.text(n_rounds, final_b, f"B: {final_b:,.0f}", color='red', fontsize=18, ha='right', va='top', fontweight='bold', bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.5'))
plt.grid(True, alpha=0.3)
plt.tight_layout()

# 주요 구간마다 금액 라벨 표시 (20회차마다)
for i in range(0, n_rounds, 20):
    plt.text(i, players['A']['history'][i], f"{players['A']['history'][i]:,.0f}", color='blue', fontsize=8, ha='center', va='bottom', fontweight='bold')
    plt.text(i, players['B']['history'][i], f"{players['B']['history'][i]:,.0f}", color='red', fontsize=8, ha='center', va='top', fontweight='bold')

# 애니메이션 함수
def animate(i):
    x = list(range(i+1))
    y_A = players['A']['history'][:i+1]
    y_B = players['B']['history'][:i+1]
    line_A.set_data(x, y_A)
    line_B.set_data(x, y_B)
    return line_A, line_B

ani = animation.FuncAnimation(fig, animate, frames=n_rounds, interval=100, blit=True)

print(f"애니메이션을 생성 중입니다...")
ani.save(gif_filename, writer='pillow', fps=10)
print(f"애니메이션이 '{gif_filename}' 파일로 저장되었습니다!")

plt.savefig(png_filename, dpi=300, bbox_inches='tight')
print(f"수익 그래프가 '{png_filename}' 파일로 저장되었습니다!")

print(f"\n최종 결과:")
print(f"A의 최종 자본: {final_a:,.0f}$")
print(f"B의 최종 자본: {final_b:,.0f}$")
print(f"총 베팅 횟수: {n_rounds}회") 