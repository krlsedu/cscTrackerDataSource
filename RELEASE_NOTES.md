# Release Notes - v26.29.001

## 🚀 Features
* **Dataset & Series:** Implementação de funcionalidades genéricas para `DatasetService`, criação de `BarDatasetService` e obtenção de informações de dataset diretamente do banco de dados.
* **Filtros e Categorização:** Adicionado suporte ao argumento `with_uncategorized` nas consultas de dataset e bar-dataset.
* **Scripts & SQL:** Criação do `ScriptsService` e otimização da query `resumo_gastos.sql` para melhores decisões de orçamento.
* **Timezone:** Adicionada função utilitária para conversão de fuso horário, integrada ao `SeriesService`.
* **Infraestrutura & Escalabilidade:** Implementação de registro de Load Balancer e suporte a Dashboards externos.
* **Observabilidade:** Integração de métricas do Prometheus com label de aplicação e adição de interceptors para monitoramento.

## 🐛 Fixes
* **SQL & Scripts:** Correção no cálculo do `ideal_value` no script `resumo_gastos.sql` e padronização de nomenclatura de variáveis (alterado `data_end` para `data_fim`).
* **Serviços:** Correção na extração de argumentos (exclusão do `with_uncategorized`), ajustes de bugs nos serviços de `BarDataset` e `Series`.
* **Repositórios:** Correção na ordem de parâmetros durante a instanciação do `HeartbeatRepository`.
* **Rede & Configuração:** Correções de URLs de comunicação (BFF) e múltiplos ajustes de mapeamento de portas na aplicação.

## 🔧 Chore
* **CI/CD & Automação:** Configuração de workflows do GitHub Actions para release, adição de `.dockerignore` e refatoração profunda do `Jenkinsfile` (versionamento automático, notificações de build e deploy automatizado).
* **Dependências:** Atualização contínua dos pacotes `csctracker-py-core` e `csctracker-queue-scheduler` no `requirements.txt`.
* **Refatoração de Código:** Limpeza de código morto, remoção de serviços não utilizados (`HttpRepository`, `LoadBalancerRegister` antigo, `PersistService`), e remoção de logs desnecessários no `FiltersRepository`.
* **Docker:** Diversos ajustes e otimizações na construção da imagem Docker e no `docker-compose.yml`.