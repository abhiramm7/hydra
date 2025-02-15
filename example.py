from flytekit import task, workflow, map_task
import pystorms.scenarios
import numpy as np
from flytekit import ImageSpec


swmm_spec = ImageSpec(
  packages=["pystorms", "numpy", "flytekit"],
  apt_packages=["curl", "wget"],
  registry="localhost:30000",
  base_image="python:3.11",
)

@task(cache=True, cache_version="1.0", container_image=swmm_spec)
def run_simulation(alpha: float) -> float:
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

@workflow()
def main(data : list[float] = [0.5, 0.6, 0.7, 0.8, 10.0]) -> list[float]:
    return map_task(run_simulation)(alpha=data)

if __name__ == "__main__":
    print(main())
