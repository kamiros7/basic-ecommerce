# basic-ecommerce

1- Leia cada script .py para verificar como executar no terminal
2- Rode todos os services (menos o payament_integrated_system, esse deve ser executado após um pedido ser criado, de forma assíncrona, para aprovar ou reprovar um pedido)
3- Abre o .index do projeto frontend para receber as notificações (se necessário, de um reload na página para receber as notificações)
4- Note, há exemplos das requisições para consultar pedidos, estoque, criar e deletar pedido
5- Uma possível ordem de execução é:
    1- Criar um pedido
    2- Deletar pedido
    3- Criar pedido
    4- Aprovar/Reprovar pedido, isso é feito com o payament_integrated_system, por isso, ele é executado apenas após um pedido ter sido criado
    5- Consultar os pedidos