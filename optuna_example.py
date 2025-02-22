import optuna
from flytekit import task, workflow, map_task
import pystorms.scenarios
import numpy as np
from flytekit import ImageSpec

swmm_spec = ImageSpec(
  packages=["pystorms", "numpy", "flytekit", "optuna"],
  apt_packages=["curl", "wget"],
  registry="localhost:30000",
  base_image="python:3.11",
)

def objective(trial: optuna.Trial):
    alpha = trial.suggest_float("alpha", 0.0, 1.0)
    scenario = pystorms.scenarios.theta()
    done = False
    beta = 0.5

    def controller(
        depths: np.ndarray,
        alpha: float = 0.50,
        beta: float = 0.50,
        MAX_DEPTH: float = 2.0,
    ) -> np.ndarray:

        # Compute the filling degree
        f = depths / MAX_DEPTH

        # Estimate the average filling degree
        f_mean = np.mean(f)

        # Compute psi
        N = len(depths)
        psi = np.zeros(N)
        for i in range(0, N):
            psi[i] = f[i] - f_mean
            if psi[i] < 0.0 - alpha:
                psi[i] = 0.0
            elif psi[i] >= 0.0 - alpha and psi[i] <= 0.0 + alpha:
                psi[i] = f_mean

        # Assign valve positions
        actions = np.zeros(N)
        for i in range(0, N):
            if depths[i] > 0.0:
                k = 1.0 / np.sqrt(2 * 9.81 * depths[i])
                action = k * beta * psi[i] / np.sum(psi)
                actions[i] = min(1.0, action)
        return actions

    while not done:
        state = scenario.state()
        action = controller(depths=state, alpha=alpha, beta=beta)
        done = scenario.step(action)

    return scenario.performance()

@task(cache=True, cache_version="1.0", container_image=swmm_spec)
def best_alpha(data: list[float]) -> float:
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=100)
    return study.best_params["alpha"]

@workflow
def optuna_workflow(data: list[float]) -> float:
    return best_alpha(data=data)

if __name__ == "__main__":
    optuna_workflow(data=[0.5, 0.6, 0.7, 0.8, 10.0])
