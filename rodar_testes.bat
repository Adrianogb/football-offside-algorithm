@echo off

echo ============================================================
echo   SIMULADOR DE IMPEDIMENTO - REGRAS FIFA (LEI 11)
echo ============================================================

:: 1. Verifica se o ambiente virtual existe
if not exist ".venv" (
    echo [AVISO] Ambiente virtual '.venv' nao encontrado.
    echo Inicializando o ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual. Certifique-se de ter o Python no PATH.
        goto fim
    )
    
    echo Instalando dependencias de requirements.txt...
    .venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar as dependencias.
        goto fim
    )
    echo [SUCESSO] Ambiente virtual configurado!
)

:: 2. Executa a logica de impedimento (modo texto)
echo.
echo [1/2] Rodando testes do algoritmo (Logica das Regras)...
echo ------------------------------------------------------------
.venv\Scripts\python.exe futbol_impedimento.py
if errorlevel 1 (
    echo [ERRO] Ocorreu um problema ao executar a logica de impedimento.
    goto fim
)

:: 3. Executa a visualizacao do campo
echo.
echo [2/2] Gerando visualizacao grafica do lance (Matplotlib)...
echo ------------------------------------------------------------
.venv\Scripts\python.exe visualizar_campo.py
if errorlevel 1 (
    echo [ERRO] Ocorreu um problema ao gerar a imagem do campo.
    goto fim
)
echo [SUCESSO] Grafico atualizado com sucesso e salvo em 'campo_impedimento.png'!

:fim
echo.
echo ============================================================
echo Execucao concluida.
pause
