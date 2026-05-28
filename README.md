# ProjetoProgramaçãoEstoque
# StockOS — Sistema de Gerenciamento de Estoque

O **StockOS** é uma aplicação web Full-Stack moderna e de alta performance projetada para o controle centralizado de inventários, auditoria de mercadorias e análise de movimentações em tempo real. 

O projeto une um ecossistema nativo de persistência em banco de dados relacional no backend com uma interface de usuário otimizada para baixa carga cognitiva no frontend.

---

## 📱 Arquitetura e Engenharia do Projeto

A aplicação foi estruturada seguindo o modelo desacoplado de uma **API RESTful**, garantindo que o processamento de dados (servidor) e a renderização visual (cliente) operem de forma independente através de requisições assíncronas (`fetch`).

* **Backend (Servidor):** Desenvolvido em **Python** utilizando o micro-framework **Flask** para o roteamento e gerenciamento dos endpoints da API.
* **Banco de Dados:** **SQLite3** para a persistência de dados relacional estável, utilizando transações ACID seguros para controle de estoque e histórico.
* **Frontend (Interface):** Construído de forma puramente nativa com **HTML5**, **CSS3** e **JavaScript Assíncrono (ES6+)**, eliminando a necessidade de frameworks pesados no lado do cliente.

### 🎨 Princípios de Design UI/UX
A interface visual foi concebida sob os pilares do **design minimalista e de alta legibilidade**, priorizando:
* **Baixa Carga Cognitiva:** Organização espacial baseada na **Lei de Miller**, estruturando as informações em blocos (chunks) lógicos de até 7 elementos para evitar a fadiga visual do usuário.
* **Alta Contraste (Dark Mode):** Paleta de cores escura e profunda com tipografia monoespaçada (`DM Mono` e `Syne`), reduzindo o cansaço ocular e focando estritamente nos dados operacionais.

---

## 🚀 Funcionalidades Principais

1.  **Dashboard de Métricas (KPIs):** Indicadores automatizados exibindo o Valor Total do Estoque, Quantidade de Itens Cadastrados, Volume de Movimentações e Alertas Críticos.
2.  **Gerenciamento do Inventário (CRUD Completo):** Inclusão, consulta, atualização e exclusão de insumos e mercadorias com cálculo automatizado de custo total.
3.  **Histórico e Auditoria:** Registro imutável de movimentações de **ENTRADA** e **SAÍDA**, documentando quantidades, justificativas lógicas (ex: Compra, Venda, Ajuste) e carimbo de data/hora.
4.  **Sistema de Alerta de Estoque Mínimo:** Identificação visual imediata e automatizada de produtos operando abaixo do limite mínimo de segurança estabelecido.

---

## 📂 Estrutura de Diretórios

Para o correto funcionamento do mecanismo de renderização do Flask, o projeto deve seguir rigorosamente a árvore estrutural abaixo:

```text
codigo/
├── app.py                  # Servidor Backend (Flask API & Regras de Negócio)
├── estoque.db              # Banco de Dados Relacional SQLite (Gerado automaticamente)
└── templates/              # Diretório reservado para arquivos de visualização
    └── index.html          # Interface Frontend (Layout, Estilos e Lógica JS)
