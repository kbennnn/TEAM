from covariance_matrix_adaptation import CMAES
import cma_config


def main():
    cma_es = CMAES()

    for generation in range(cma_config.GENERATIONS):
        cma_es.run_generation(cma_config.DAYS, generation)


if __name__ == "__main__":
    main()