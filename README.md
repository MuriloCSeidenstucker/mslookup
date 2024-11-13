
# MSLookup - Automação para Obtenção de Registros de Medicamentos

## Descrição
Este projeto foi criado inicialmente como um estudo em Python e evoluiu para uma solução prática para um problema real enfrentado em licitações de medicamentos. Ele automatiza a busca e o download dos registros de medicamentos no site da ANVISA, utilizando o site SMERP e planilhas disponibilizadas pela ANVISA. Essa automação é útil em cenários onde são exigidos registros dos medicamentos, agilizando e facilitando o processo de pesquisa e geração de PDFs dos registros.

## Motivação
Enquanto trabalhava como responsável por licitações de uma distribuidora de medicamentos, enfrentei o desafio de obter e imprimir registros de medicamentos exigidos em muitos editais. O processo tinha várias etapas e era manual, tornando-o repetitivo e demorado. Portanto, desenvolvi uma automação para esta tarefa, envolvendo o uso do Selenium para realizar a pesquisa no navegador e extrair os registros. Ao longo do desenvolvimento, implementei filtros para lidar com descrições de medicamentos variadas e identifiquei laboratórios que eram parceiros para melhorar a precisão da pesquisa.

## Pré-requisitos
- **Sistema operacional:** Windows (não testado em macOS ou Linux).
- **Gerenciador de dependências:** [Poetry](https://python-poetry.org/) (para instalação de dependências).
- **Python**: Versão 3.9 ou superior.

## Instalação
1. Clone o repositório:
   
   ```
   git clone https://github.com/MuriloCSeidenstucker/mslookup.git
   cd mslookup
   ```

2. Instale as dependências com Poetry:
   
   ```
   poetry install
   ```

## Uso

1. Após instalar, inicie o app com o comando:
   
    ```
    poetry run python .\mslookup\main.py
    ```

Ou, se configurado, utilize o script:

    mslookup_start

2. Na interface que será aberta, selecione uma planilha Excel contendo **três colunas obrigatórias:**

- Números dos itens
- Descrição dos medicamentos
- Marca/Laboratório

3. O aplicativo tentará reconhecer automaticamente os nomes das colunas; caso contrário, o usuário deve preenchê-los manualmente.

4. Clique em **Buscar Registros** para iniciar a automação. A aplicação seguirá as seguintes etapas:

- **Processamento da Planilha:** Extração das substâncias e concentrações dos medicamentos a partir das descrições.
- **Busca dos Registros:** Busca de registros no SMERP e ANVISA.
- **Download dos PDFs:** Tentativa de obtenção e download dos PDFs dos registros.
- **Geração do Relatório:** Criação de um relatório Excel com os registros encontrados e status de cada PDF.

5. O relatório será salvo na pasta raiz do projeto, e os PDFs serão salvos na pasta Downloads do computador.

## Contato

Fico à disposição para dúvidas, sugestões e colaborações. Entre em contato pelos seguintes canais:

- **Email:** [murilocampos.004@gmail.com](mailto:seu-email@example.com) – Para dúvidas específicas sobre o projeto ou propostas de colaboração.
- **LinkedIn:** [murilocseidenstucker](https://www.linkedin.com/in/murilocseidenstucker/) – Siga-me no LinkedIn para atualizações sobre este e outros projetos.
- **GitHub:** [MuriloCSeidenstucker](https://github.com/MuriloCSeidenstucker) – Confira outros repositórios e contribua com feedbacks e sugestões.

Se preferir, crie uma [Issue](https://github.com/MuriloCSeidenstucker/mslookup/issues) neste repositório para relatar bugs ou sugerir melhorias diretamente por aqui.

Agradeço por visitar o projeto, e espero que ele seja útil para você!
