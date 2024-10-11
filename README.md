# projeto_impacta
Software Product: Analysis, Specification, Project &amp; Implementation 202402 - EAD - ADS 5A - Pojeto Impacta Pub

1. Visão Geral do Projeto

O projeto consiste em um sistema de gerenciamento de pedidos para um bar, desenvolvido utilizando Flask como framework back-end, PostgreSQL como banco de dados e Tailwind CSS para estilização do front-end. O sistema foi projetado para permitir que os clientes façam pedidos, adicionem itens a uma comanda e finalizem seus pedidos, enquanto o administrador tem acesso a um painel de controle para gerenciar produtos, pedidos e clientes.

2. Objetivos do Sistema

- Facilitar a gestão de pedidos em um bar, permitindo que os clientes criem, visualizem e finalizem pedidos diretamente pelo sistema.
- Oferecer um painel administrativo para que o gerente do bar ou administrador gerencie os produtos disponíveis, pedidos e clientes.
- Automatizar o fluxo de pedidos e fornecer feedback imediato aos clientes sobre o status de seus pedidos.
  
3. Tecnologias Utilizadas

Flask: Framework utilizado para construir a lógica do back-end e gerenciar as rotas HTTP.
PostgreSQL: Banco de dados relacional utilizado para armazenar informações de clientes, pedidos, produtos e itens de pedido. Feito hospedagem do banco de dados em nuvem pela plataforma TEMBO.IO
-Tailwind CSS: Framework CSS utilizado para estilização rápida e responsiva das páginas do sistema.
-Bcrypt: Biblioteca para o hashing de senhas de usuários, garantindo a segurança dos dados.

4. Funcionalidades Principais

4.1 Funcionalidades para o Cliente

Cadastro e Login: Clientes podem se cadastrar e fazer login utilizando suas credenciais (email e senha). Um sistema de hash (Bcrypt) é utilizado para armazenar as senhas de maneira segura.
  
Criação de Pedido: Após o login, o cliente pode iniciar um pedido e adicionar itens a uma comanda antes de enviar o pedido final para o bar.

Adição de Itens ao Pedido: O cliente pode visualizar uma lista de produtos disponíveis e escolher a quantidade de cada produto para adicionar ao seu pedido.

Finalização de Pedido: Quando o cliente adiciona todos os itens desejados, ele pode finalizar o pedido, e o sistema atualiza o banco de dados e exibe uma mensagem de sucesso.

Mensagem de Confirmação: Após finalizar o pedido, o cliente visualiza uma mensagem de "Pedido enviado com sucesso, aguarde!" na tela.

4.2 Funcionalidades para o Administrador

Login como Administrador: O sistema permite que o administrador faça login com as credenciais `admin/admin` e seja redirecionado para o painel de controle administrativo.

Painel de Controle (Dashboard): No painel, o administrador pode:
  Listar Clientes: Ver todos os clientes cadastrados no sistema.
  Listar Pedidos: Ver todos os pedidos realizados pelos clientes.
  Cadastrar Produtos: Adicionar novos produtos ao catálogo disponível para pedidos.

Gerenciamento de Produtos: O administrador pode cadastrar novos produtos, que ficam disponíveis para os clientes na tela de criação de pedidos.

5. Arquitetura do Sistema

Front-end: Desenvolvido utilizando HTML, CSS com Tailwind e JavaScript. O front-end é simples e focado na funcionalidade e experiência do usuário, com uma interface responsiva.
  
Back-end: Utilizado Flask para o gerenciamento das rotas, sessões e validação de usuários. O back-end é responsável por toda a lógica do sistema, incluindo o controle de pedidos e autenticação de usuários.

Banco de Dados: O sistema utiliza PostgreSQL como banco de dados. As tabelas principais incluem:
  Cliente: Informações dos clientes cadastrados.
  Pedido: Detalhes sobre os pedidos realizados pelos clientes, como valor total e status.
  ItemPedido: Tabela intermediária que armazena os itens de cada pedido.
  Produto: Produtos disponíveis para pedido, com nome e preço.

6. Fluxo de Trabalho

1. Cadastro e Login de Clientes:
   - Clientes podem se cadastrar e fazer login.
   - O login de administrador redireciona para o painel administrativo.

2. Criação de Pedido:
   - O cliente cria um pedido e adiciona itens de produtos à comanda.
   - Uma tabela na tela mostra os itens adicionados, permitindo que o cliente revise o pedido antes de enviá-lo.

3. Finalização do Pedido:
   - Ao finalizar o pedido, o sistema o armazena no banco de dados e exibe uma mensagem de sucesso ao cliente.
   - O pedido é marcado como "finalizado" no banco de dados.

4. Gerenciamento pelo Administrador:
   - O administrador pode acessar o painel, listar pedidos, gerenciar clientes e adicionar produtos ao catálogo.

7. Desafios Enfrentados e Soluções

- Autenticação e Redirecionamento de Administrador:
  - Solução: Implementação de lógica específica para o administrador com credenciais `admin/admin`, redirecionando para o painel administrativo quando o login for feito corretamente.

- Fluxo de Pedido com Adição de Itens:
  - Desafio: Garantir que o cliente possa adicionar vários itens a um pedido, revisar e só então enviar o pedido.
  - Solução: Implementação de uma tabela que exibe os itens adicionados, com a possibilidade de remover itens e revisar antes de finalizar o pedido.

- Segurança:
  - Utilização de `bcrypt` para garantir que as senhas dos clientes sejam armazenadas de maneira segura no banco de dados.
  
8. Testes e Validação

- O sistema foi testado para garantir que o fluxo de trabalho funcione corretamente para clientes e administradores.
- Foram realizados testes de:
  - Validação de formulários (todos os campos obrigatórios devem ser preenchidos).
  - Autenticação e controle de sessão (manter a segurança dos dados de login e permitir acesso a páginas específicas apenas para usuários autorizados).
  - Integração com o banco de dados (garantir que os dados sejam corretamente inseridos, atualizados e visualizados).

9. Possíveis Melhorias Futuras

- Adição de funcionalidades de pagamento: Implementar uma funcionalidade que permita que os clientes façam o pagamento online após finalizarem o pedido.
- Melhorias na UI: Implementar um design mais sofisticado e amigável para tornar o sistema mais atrativo.
- Histórico de Pedidos: Permitir que o cliente visualize o histórico de pedidos anteriores e seus detalhes.
- Controle de Estoque: Adicionar um sistema de controle de estoque que diminua a quantidade disponível de produtos conforme os pedidos são realizados.

10. Conclusão

O sistema de gerenciamento de pedidos para bar foi desenvolvido com o objetivo de facilitar o fluxo de trabalho em um ambiente de bar, tanto para clientes quanto para o administrador. O sistema oferece uma maneira eficiente de criar, gerenciar e finalizar pedidos, além de garantir que o administrador tenha controle sobre o catálogo de produtos e a gestão de clientes e pedidos.

Este projeto pode ser facilmente adaptado para outros setores de serviços, como restaurantes e cafés, e há muitas possibilidades de expansão e aprimoramento do sistema para atender a necessidades específicas.
