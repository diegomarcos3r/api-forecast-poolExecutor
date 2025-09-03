import numpy as np
from typing import List, Dict



class Forecast:

    """
    Classe para simulação de Monte Carlo de previsão de semanas para concluir o backlog.
    """

    def __init__(self, nr_simulations: int, backlog_min: int, backlog_max:int, throughput: List[int]):
        self.nr_simulations = nr_simulations
        self.backlog_min = backlog_min
        self.backlog_max = backlog_max
        self.throughput = throughput

    def run_simulation(self) -> List[int]:

        """
            Rodar uma simulação monte carlo.
        """

        forecast_weeks = []
        for _ in range(self.nr_simulations):

            backlog_done = 0
            random_weeks = 0
            backlog = np.random.randint(self.backlog_min, self.backlog_max + 1)

            while backlog_done < backlog:
                random_throughput = np.random.choice(self.throughput)
                backlog_done = random_throughput + backlog_done
                random_weeks = random_weeks + 1

            forecast_weeks.append(random_weeks)
    
        return forecast_weeks

    @staticmethod
    def calculate_percentiles(forecast_weeks:List[int],percentiles:List[int]) -> dict:

        
        """
            Calcular os percentis para o resultado da simulação monte carlo.
        """

        if len(forecast_weeks) == 0 or len(percentiles) == 0:
            raise ValueError("Os argumentos não podem vir vazios.Não é possível calcular os percentis.")
    
        return {p: int(np.percentile(forecast_weeks, p)) for p in percentiles}

    def format_forecast_response(self,p50:int,p75:int,p85:int,p95:int) -> dict:

        """
            Estruturar a resposta da requisição do cliente.
        """

        return {
        
            'Backlog-min': self.backlog_min,
            'Backlog-max':self.backlog_max,
            'Throughput':self.throughput,
            'Simulations':self.nr_simulations,
            'Percentil-50':p50,
            'Percentil-75':p75,
            'Percentil-85':p85,
            'Percentil-95':p95

        }

    









