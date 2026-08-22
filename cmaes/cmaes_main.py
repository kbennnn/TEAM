from cmaes.covariance_matrix_adaptation import CMAES
import cmaes.cmaes_config as cmaes_config


def main():
    cma_es = CMAES()

    for generation in range(cmaes_config.GENERATIONS):
        cma_es.run_generation(cmaes_config.DAYS, generation)


if __name__ == "__main__":
    main()