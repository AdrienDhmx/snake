from multiprocessing import Pool
from random import seed
from statistics import mean, stdev
import matplotlib.pyplot as plt

from shortSnake import ShortSnake
from greedyPlayer import GreedyPlayer
from action import Action

SIZE = 5
EPS = 0.1
RUNS = 2000
GAMMAS = [0, 0.1, 0.5, 0.9, 1]
GAMMAS_SEARCH = [i / 20 for i in range(21)]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]


def exercice1():
    snake = ShortSnake(5)
    print(snake)

    snake.move(Action.LEFT)
    print(snake)

    snake.move(Action.LEFT)
    print(snake)

    snake.move(Action.LEFT)
    print(snake)

    snake.move(None)
    print(snake)

    snake.move(Action.RIGHT)
    print(snake)

    snake.move(None)
    print(snake)


def play(player, snake, steps):
    rewards = []

    for step in range(steps):
        action = player.get_action()
        old_score = snake.score
        snake.move(action)
        reward = snake.score - old_score
        player.reward(action, reward)
        rewards.append(reward)

    return rewards


def simulate(gamma, steps, runs, size=SIZE, longueur=1):
    seed(42)
    total_rewards = [0] * steps
    run_means = []

    for run in range(runs):
        snake = ShortSnake(size, longueur)
        player = GreedyPlayer(snake, EPS, gamma)
        rewards = play(player, snake, steps)

        for step in range(steps):
            total_rewards[step] += rewards[step]
        run_means.append(mean(rewards))

    avg_rewards = [total / runs for total in total_rewards]
    return avg_rewards, run_means


def simulate_all(jobs):
    with Pool() as pool:
        return pool.starmap(simulate, jobs)


def moving_average(values, window):
    averages = []
    total = 0

    for i in range(len(values)):
        total += values[i]
        if i >= window:
            total -= values[i - window]
        if i >= window - 1:
            averages.append(total / window)

    return averages


def standard_error(run_means):
    return stdev(run_means) / len(run_means) ** 0.5


def save_plot(title, xlabel, ylabel, filename):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha=0.3)
    plt.savefig(filename, dpi=150)
    plt.close()


def exercice3_9():
    snake = ShortSnake(SIZE)
    player = GreedyPlayer(snake, EPS)
    play(player, snake, 1000)
    print(snake)


def exercice3_10():
    seed(42)
    snake = ShortSnake(SIZE)
    player = GreedyPlayer(snake, EPS)
    rewards = play(player, snake, 1000)

    print(f"Q10 : score final = {snake.score}, fruits = {rewards.count(10)}, bords = {rewards.count(-10)}")

    plt.plot(rewards, color=COLORS[0], linewidth=1)
    save_plot("Récompense d'une seule IA", "Étape", "Récompense", "image/Exercice3_10.png")


def exercice3_11():
    counts = [1, 10, 100, 500, 2000, 10000]
    results = simulate_all([(0.5, 1000, count) for count in counts])

    print("Q11 : relances, écart-type de la courbe, erreur type de la moyenne")
    for count, (avg_rewards, run_means) in zip(counts, results):
        error = standard_error(run_means) if count > 1 else float("nan")
        print(f"{count} : {stdev(avg_rewards):.3f}, {error:.4f}")

    shown = [1, 10, 100, 2000]
    figure, axes = plt.subplots(2, 2, sharex=True, figsize=(8, 6))
    for ax, count in zip(axes.flat, shown):
        avg_rewards = results[counts.index(count)][0]
        ax.plot(avg_rewards, color=COLORS[0], linewidth=0.8)
        ax.set_title(f"{count} relance(s)")
        ax.grid(alpha=0.3)
    figure.supxlabel("Étape")
    figure.supylabel("Récompense moyenne")
    figure.tight_layout()
    figure.savefig("image/Exercice3_11.png", dpi=150)
    plt.close(figure)


def compare_gammas(steps, window, filename, longueur=1):
    results = simulate_all([(gamma, steps, RUNS, SIZE, longueur) for gamma in GAMMAS])
    last = steps // 10

    print(f"Comparaison sur {steps} étapes : gamma, moyenne totale, erreur type, moyenne fin")
    for i in range(len(GAMMAS)):
        avg_rewards, run_means = results[i]
        print(f"{GAMMAS[i]} : {mean(avg_rewards):.3f}, {standard_error(run_means):.3f}, {mean(avg_rewards[-last:]):.3f}")

        smooth = moving_average(avg_rewards, window)
        x = range(window - 1, steps)
        plt.plot(x, smooth, color=COLORS[i], linewidth=1.5, label=f"γ = {GAMMAS[i]}")

    plt.legend()
    save_plot(f"Récompense moyenne selon γ ({RUNS} relances)", "Étape", f"Récompense moyenne (fenêtre de {window})", filename)


def search_gamma(steps, runs, filename, longueur=1):
    results = simulate_all([(gamma, steps, runs, SIZE, longueur) for gamma in GAMMAS_SEARCH])
    last = steps // 10
    means = []
    errors = []

    print(f"Recherche sur {steps} étapes, {runs} relances : gamma, moyenne totale, erreur type, moyenne fin")
    for i in range(len(GAMMAS_SEARCH)):
        avg_rewards, run_means = results[i]
        means.append(mean(avg_rewards))
        errors.append(1.96 * standard_error(run_means))
        print(f"{GAMMAS_SEARCH[i]:.2f} : {means[i]:.4f}, {standard_error(run_means):.4f}, {mean(avg_rewards[-last:]):.4f}")

    plt.errorbar(GAMMAS_SEARCH, means, yerr=errors, color=COLORS[0], marker="o", markersize=4, linewidth=1.5, capsize=3)
    save_plot(f"Récompense moyenne selon γ ({steps} étapes)", "γ", "Récompense moyenne par étape", filename)


def compare_sizes():
    jobs = []
    for steps in [1000, 10000]:
        for gamma in [0, 0.5, 0.9]:
            jobs.append((gamma, steps, 500, 10))

    results = simulate_all(jobs)

    print("Grille 10 x 10 : étapes, gamma, moyenne totale, moyenne début, moyenne fin")
    for job, (avg_rewards, run_means) in zip(jobs, results):
        gamma, steps = job[0], job[1]
        last = steps // 10
        print(f"{steps}, {gamma} : {mean(avg_rewards):.3f}, {mean(avg_rewards[:last]):.3f}, {mean(avg_rewards[-last:]):.3f}")


def exercice4_5_une_ia():
    seed(42)
    snake = ShortSnake(SIZE, 2)
    player = GreedyPlayer(snake, EPS)
    rewards = play(player, snake, 1000)

    print(f"Une IA : score final = {snake.score}, fruits = {rewards.count(10)}, bords = {rewards.count(-10)}")

    plt.plot(rewards, color=COLORS[0], linewidth=1)
    save_plot("Récompense d'une seule IA (serpent de taille 2)", "Étape", "Récompense", "image/Exercice4_5_1.png")


def exercice4_5_moyenne():
    avg_rewards, run_means = simulate(0.5, 1000, RUNS, SIZE, 2)

    print(f"Moyenne sur {RUNS} relances : {mean(avg_rewards):.3f}, erreur type {standard_error(run_means):.3f}")

    plt.plot(avg_rewards, color=COLORS[0], linewidth=0.8)
    save_plot(f"Récompense moyenne (serpent de taille 2, {RUNS} relances)", "Étape", "Récompense moyenne", "image/Exercice4_5_2.png")


def exercice4_6():
    steps = 10000
    window = 200
    longueurs = [1, 2]
    results = simulate_all([(0.5, steps, RUNS, SIZE, longueur) for longueur in longueurs])

    print("Comparaison des tailles : taille, moyenne totale, erreur type, moyennes par tranche de 1000 étapes")
    for i in range(len(longueurs)):
        avg_rewards, run_means = results[i]
        slices = [mean(avg_rewards[start:start + 1000]) for start in range(0, steps, 1000)]
        print(longueurs[i], f"{mean(avg_rewards):.4f}", f"{standard_error(run_means):.4f}", [round(value, 3) for value in slices])

        smooth = moving_average(avg_rewards, window)
        plt.plot(range(window - 1, steps), smooth, color=COLORS[i], linewidth=1.5, label=f"Taille {longueurs[i]}")

    plt.legend()
    save_plot(f"Récompense moyenne selon la taille du serpent (γ = 0.5, {RUNS} relances)", "Étape", f"Récompense moyenne (fenêtre de {window})", "image/Exercice4_6.png")


def exercice3():
    exercice3_9()
    exercice3_10()
    exercice3_11()
    compare_gammas(1000, 50, "image/Exercice3_12.png")
    search_gamma(1000, 10000, "image/Exercice3_13.png")
    compare_gammas(10000, 200, "image/Exercice3_14_1.png")
    search_gamma(10000, 2000, "image/Exercice3_14_2.png")
    compare_sizes()


def exercice4():
    exercice4_5_une_ia()
    exercice4_5_moyenne()
    compare_gammas(1000, 50, "image/Exercice4_5_3.png", 2)
    search_gamma(1000, 10000, "image/Exercice4_5_4.png", 2)
    compare_gammas(10000, 200, "image/Exercice4_5_5.png", 2)
    search_gamma(10000, 2000, "image/Exercice4_5_6.png", 2)
    exercice4_6()


def main():
    exercice3()
    exercice4()


if __name__ == "__main__":
    main()
