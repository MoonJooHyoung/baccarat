import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 대신 Agg 백엔드 사용
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import numpy as np

# 바카라 승률 설정 (실제 바카라 승률)
player_win_prob = 0.4462  # 플레이어 승률
banker_win_prob = 0.4586  # 뱅커 승률
tie_prob = 0.0952  # 타이 확률 (이 시뮬레이션에서는 무시)

# 초기 설정
initial_bet = 100  # 초기 베팅 금액

# 시뮬레이션 설정
rounds = 50
a_total = 0
b_total = 0
a_bet = initial_bet
b_bet = initial_bet
a_direction = "Player"
b_direction = "Banker"

a_balance_history = [a_total]
b_balance_history = [b_total]
results = []

for rnd in range(rounds):
    result = random.choices(["Player", "Banker"], weights=[player_win_prob, banker_win_prob])[0]

    if a_direction == result:
        a_total += a_bet
        b_total -= b_bet
        a_bet = a_total
        b_bet = initial_bet
        a_direction = "Banker"
        b_direction = "Player"
    else:
        a_total -= a_bet
        b_total += b_bet
        b_bet = b_total
        a_bet = initial_bet
        a_direction = "Player"
        b_direction = "Banker"

    a_balance_history.append(a_total)
    b_balance_history.append(b_total)
    results.append((a_total, b_total))

# 애니메이션 함수 정의
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, rounds)
ax.set_ylim(min(min(a_balance_history), min(b_balance_history)) - 50,
            max(max(a_balance_history), max(b_balance_history)) + 50)
line_a, = ax.plot([], [], 'b-o', label='A 수익', linewidth=2, markersize=4)
line_b, = ax.plot([], [], 'r-x', label='B 수익', linewidth=2, markersize=4)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.set_title("A vs B 수익 흐름 애니메이션 (50판)", fontsize=14, fontweight='bold')
ax.set_xlabel("회차", fontsize=12)
ax.set_ylabel("수익 ($)", fontsize=12)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

def init():
    line_a.set_data([], [])
    line_b.set_data([], [])
    return line_a, line_b

def update(frame):
    x = list(range(frame + 1))
    y_a = a_balance_history[:frame + 1]
    y_b = b_balance_history[:frame + 1]
    line_a.set_data(x, y_a)
    line_b.set_data(x, y_b)
    return line_a, line_b

ani = animation.FuncAnimation(fig, update, frames=rounds + 1, init_func=init,
                              blit=True, interval=300, repeat=False)

plt.tight_layout()

# 애니메이션을 GIF로 저장
print("애니메이션을 생성 중입니다...")
ani.save('baccarat_animation.gif', writer='pillow', fps=3)
print("애니메이션이 'baccarat_animation.gif' 파일로 저장되었습니다!")

# 결과 출력
print(f"\n최종 결과:")
print(f"A의 최종 수익: ${a_total}")
print(f"B의 최종 수익: ${b_total}")
print(f"총 베팅 횟수: {rounds}회")

# 수익 그래프도 저장
plt.figure(figsize=(12, 6))
plt.plot(range(rounds + 1), a_balance_history, 'b-o', label='A 수익', linewidth=2, markersize=4)
plt.plot(range(rounds + 1), b_balance_history, 'r-x', label='B 수익', linewidth=2, markersize=4)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
plt.title("A vs B 수익 흐름 (50판)", fontsize=14, fontweight='bold')
plt.xlabel("회차", fontsize=12)
plt.ylabel("수익 ($)", fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('baccarat_results.png', dpi=300, bbox_inches='tight')
print("수익 그래프가 'baccarat_results.png' 파일로 저장되었습니다!") 