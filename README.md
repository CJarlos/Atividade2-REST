# Atividade2-REST
Atividade Prática: Sistema de Biblioteca com Arquitetura REST - Microsserviços

# API de Gerenciamento de Biblioteca Digital

Esta é uma API RESTful para gerenciar livros, autores e empréstimos.

## Instalação

1.  Clone o repositório.
2.  Crie um ambiente virtual: `python -m venv venv`
3.  Ative o ambiente: `source venv/bin/activate` (Linux/macOS) ou `venv\Scripts\activate` (Windows)
4.  Instale as dependências: `pip install Flask`

## Execução

Para iniciar o servidor de desenvolvimento, execute:

```bash
# python app.py

````

# Relatório de Design da API
## 1. Decisões de Arquitetura e Design

A escolha da arquitetura REST (Representational State Transfer) foi motivada por sua simplicidade, escalabilidade e ampla adoção no mercado. REST nos permite modelar o sistema como um conjunto de recursos (Livros, Autores, etc.) que podem ser manipulados através de uma interface uniforme (métodos HTTP).

A utilização de JSON como formato de dados padrão garante a interoperabilidade com uma vasta gama de clientes (web, mobile, outros serviços). Os códigos de status HTTP são empregados para comunicar o resultado das operações de forma padronizada, e o HATEOAS (Hypermedia as the Engine of Application State) é implementado para tornar a API auto-descritiva e facilitar a navegação pelo cliente.

## 2. Estrutura dos Recursos

Os recursos foram modelados de forma a refletir as entidades do domínio. As URIs foram definidas no plural para representar coleções (/livros, /autores), uma convenção que melhora a legibilidade. As relações entre recursos são representadas por objetos aninhados (como o autor dentro de um livro) para simplificar as consultas mais comuns, evitando a necessidade de múltiplas requisições para obter dados relacionados. Em cenários mais complexos, poderíamos usar apenas os IDs e fornecer endpoints específicos para obter os dados relacionados, como /livros/{id}/autor.
