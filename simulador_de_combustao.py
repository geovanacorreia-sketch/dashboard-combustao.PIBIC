#SIMULADOR DE COMBUSTÃO
#BANCO DE DADOS:
# Dicionário com dados dos combustíveis 
COMBUSTIVEIS = {
    "CH4": {
        "n_C": 1, "n_H": 4, "n_O": 0, 
        "delta_Hf": -74.8, "delta_Hr": -802.34, 
        "a": 3.43e-02, "b": 5.47e-05, "c": 3.66e-09, "d": -1.10e-11
    },
    "C2H6": {
        "n_C": 2, "n_H": 6, "n_O": 0, 
        "delta_Hf": -84.7, "delta_Hr": -1427.87, 
        "a": 4.94e-02, "b": 1.39e-04, "c": -5.82e-08, "d": 7.28e-12
    },
    "C3H8": {
        "n_C": 3, "n_H": 8, "n_O": 0, 
        "delta_Hf": -103.8, "delta_Hr": -2043.96, 
        "a": 6.80e-02, "b": 2.26e-04, "c": -1.31e-07, "d": 3.17e-11
    },
    "C4H10": {
        "n_C": 4, "n_H": 10, "n_O": 0, 
        "delta_Hf": -125.7, "delta_Hr": -2658.45, 
        "a": 9.23e-02, "b": 2.79e-04, "c": -1.55e-07, "d": 3.50e-11
    },
    "C5H12": {
        "n_C": 5, "n_H": 12, "n_O": 0, 
        "delta_Hf": -146.4, "delta_Hr": -3272.04, 
        "a": 1.15e-01, "b": 3.41e-04, "c": -1.90e-07, "d": 4.23e-11
    },
    "C6H14": {
        "n_C": 6, "n_H": 14, "n_O": 0, 
        "delta_Hf": -167.2, "delta_Hr": -3886.73, 
        "a": 1.37e-01, "b": 4.09e-04, "c": -2.39e-07, "d": 5.77e-11
    },
    "C2H2": {
        "n_C": 2, "n_H": 2, "n_O": 0, 
        "delta_Hf": 226.7, "delta_Hr": -1257.09, 
        "a": 4.23e-02, "b": 4.39e-05, "c": -3.02e-08, "d": 9.07e-12
    },
    "CH4O": {
        "n_C": 1, "n_H": 4, "n_O": 1, 
        "delta_Hf": -201.2, "delta_Hr": -588.48, 
        "a": 4.29e-02, "b": 7.60e-05, "c": -2.93e-08, "d": 4.18e-12
    },
    "C2H6O": {
        "n_C": 2, "n_H": 6, "n_O": 1, 
        "delta_Hf": -234.8, "delta_Hr": -1145.27, 
        "a": 6.13e-02, "b": 1.57e-04, "c": -8.74e-08, "d": 1.98e-11
    },
    "i-C4H10": {
        "n_C": 4, "n_H": 10, "n_O": 0, 
        "delta_Hf": -134.2, "delta_Hr": -2648.15, 
        "a": 9.04e-02, "b": 2.85e-04, "c": -1.65e-07, "d": 3.85e-11
    }
}
# Dicionário com dados dos gases e produtos 
GASES_PRODUTOS = {
    "O2":  {"delta_Hf": 0.0,    "a": 2.91e-02, "b": 1.16e-05, "c": -6.08e-09, "d": 1.31e-12},
    "N2":  {"delta_Hf": 0.0,    "a": 2.90e-02, "b": 2.20e-06, "c": 5.72e-09,  "d": -2.87e-12},
    "CO2": {"delta_Hf": -393.5, "a": 3.61e-02, "b": 4.23e-05, "c": -2.89e-08, "d": 7.46e-12},
    "H2O": {"delta_Hf": -241.8, "a": 3.35e-02, "b": 6.88e-06, "c": 7.60e-09,  "d": -3.59e-12},
    "CO":  {"delta_Hf": -110.5, "a": 2.90e-02, "b": 4.11e-06, "c": 3.55e-09,  "d": -2.22e-12},
    "H2":  {"delta_Hf": 0.0,    "a": 2.88e-02, "b": 7.65e-08, "c": 3.29e-09,  "d": -8.70e-13}
}
# Funcões Termodinâmicas
# Função para calcular H de uma espécie gasosa variando a Temperatura (em °C ou K)
def calcular_entalpia_sensivel(especie_dados, T1, T2):
    a = especie_dados["a"]
    b = especie_dados["b"]
    c = especie_dados["c"]
    d = especie_dados["d"]    
    # Integral de Cp dT de T1 até T2
    delta_H = (a * (T2 - T1) + 
               (b / 2) * (T2**2 - T1**2) + 
               (c / 3) * (T2**3 - T1**3) + 
               (d / 4) * (T2**4 - T1**4))
    return delta_H
def obter_dados_especie(nome):
    if nome in COMBUSTIVEIS:
        return COMBUSTIVEIS[nome]
    if nome in GASES_PRODUTOS:
        return GASES_PRODUTOS[nome]
    raise ValueError(f"Espécie '{nome}' não encontrada.")
def calcular_entalpia_total(especie_dados, T):
    """
    Calcula H = delta_Hf + delta_Hsens (kJ/mol)
    """
    delta_Hf = especie_dados["delta_Hf"]
    h_sens = calcular_entalpia_sensivel(especie_dados, 25, T)  # Adotando 25 C como referência de temperatura
    return delta_Hf + h_sens
def calcular_balanco_massa(combustivel_nome, mols_comb_entrada, excesso_ar, conversao_pct, seletividade_co2_pct):
    """
    Realiza o balanço de massa completo com base em conversão e seletividade.
    Conversão e Seletividade passadas em porcentagem (0 a 100%).
    """
    if not (0 <= conversao_pct <= 100):
        raise ValueError("Conversão deve estar entre 0 e 100%")
    if not (0 <= seletividade_co2_pct <= 100):
        raise ValueError("Seletividade deve estar entre 0 e 100%")
    if excesso_ar < 0:
        raise ValueError("Excesso de ar não pode ser negativo")
    if mols_comb_entrada <= 0:
        raise ValueError("A vazão de combustível deve ser maior que zero")
    dados = COMBUSTIVEIS[combustivel_nome]
    n = dados["n_C"]
    m = dados["n_H"]
    p = dados["n_O"]
    conversao = conversao_pct / 100
    seletividade = seletividade_co2_pct / 100
    # OXIGÊNIO TEÓRICO
    # CxHyOz : O2 = x + y/4 - z/2
    o2_teorico_por_mol = (n +m / 4- p / 2)
    o2_teorico_total = ( mols_comb_entrada * o2_teorico_por_mol)
    o2_entrada =  o2_teorico_total * (1 + excesso_ar / 100)
    n2_entrada = o2_entrada * 3.76
    ar_real = o2_entrada + n2_entrada
     # COMBUSTÍVEL REAGIDO
    mols_comb_reagido = mols_comb_entrada * conversao
    mols_comb_nao_reagiu = mols_comb_entrada - mols_comb_reagido
    # Separação do combustível pelas rotas (Seletividade)
    mols_rota_completa = mols_comb_reagido * seletividade
    mols_rota_incompleta = mols_comb_reagido * (1 - seletividade)
     # ROTA COMPLETA: CxHyOz + O2 -> CO2 + H2O
    co2_r1 = mols_rota_completa * n
    h2o_r1 = (mols_rota_completa* (m / 2))
    o2_r1 = (mols_rota_completa* (n + m/ 4 - p / 2))
     # ROTA INCOMPLETA:CxHyOz + O2 -> CO + H2O
    co_r2 = (mols_rota_incompleta* n)
    h2o_r2 = (mols_rota_incompleta* (m / 2))
    o2_r2 = (mols_rota_incompleta* (n / 2+ m / 4- p / 2))
    o2_consumido = (o2_r1+ o2_r2)
    o2_saida = max(0,o2_entrada - o2_consumido)
    correntes_saida = {
        combustivel_nome:
            mols_comb_nao_reagiu,
        "CO2":
            co2_r1,
        "CO":
            co_r2,
        "H2O":
            h2o_r1 + h2o_r2,
        "O2":
            o2_saida,
        "N2":
            n2_entrada
    }
    total_saida = sum(correntes_saida.values())
    fracoes_molares_umida = {
        especie: (vazao / total_saida) * 100
        for especie, vazao in correntes_saida.items()
    }
    #Calcular base seca (excluindo H2O)
    correntes_saida_seca = {
        especie: vazao for especie, vazao in correntes_saida.items() 
        if especie != "H2O"
    }
    total_seco = sum(correntes_saida_seca.values())
    fracoes_molares_seca = {}
    for especie, vazao in correntes_saida_seca.items():
        if total_seco > 0:
            fracoes_molares_seca[especie] = (vazao / total_seco) * 100
        else:
            fracoes_molares_seca[especie] = 0
    return {
        "correntes_saida": correntes_saida,
        "fracoes_molares_umida": fracoes_molares_umida,  
        "fracoes_molares_seca": fracoes_molares_seca,    
        "correntes_saida_seca": correntes_saida_seca,    
        "o2_teorico": o2_teorico_total,
        "o2_real": o2_entrada,
        "n2_real": n2_entrada,
        "ar_real": ar_real,
        "combustivel_reagido": mols_comb_reagido,
        "combustivel_nao_reagido": mols_comb_nao_reagiu,
        "conversao": conversao_pct,
        "seletividade": seletividade_co2_pct,
        "total_saida": total_saida,
        "total_seco": total_seco,  
        "agua_produzida": correntes_saida["H2O"] 
    }
#Balanço de Energia
def calcular_delta_hr(combustivel_nome, seletividade_pct):
    dados = COMBUSTIVEIS[combustivel_nome]
    x = dados["n_C"]
    y = dados["n_H"]
    S = seletividade_pct / 100
    hf_comb = dados["delta_Hf"]
    hf_co2 = GASES_PRODUTOS["CO2"]["delta_Hf"]
    hf_co = GASES_PRODUTOS["CO"]["delta_Hf"]
    hf_h2o = GASES_PRODUTOS["H2O"]["delta_Hf"]
    delta_hr = (x * S * hf_co2 + x * (1 - S) * hf_co + (y / 2) * hf_h2o - hf_comb)
    return delta_hr
def calcular_q_chamine(correntes_saida,T_chamine):
    q_chamine = 0
    for especie, vazao in correntes_saida.items():
        dados = obter_dados_especie(especie)
        h_sens = calcular_entalpia_sensivel(dados,25, T_chamine)
        q_chamine += vazao * h_sens
    return q_chamine
def calcular_q_comb(combustivel_nome,combustivel_reagido,seletividade_pct):
    delta_hr = calcular_delta_hr(combustivel_nome,seletividade_pct)
    q_comb = abs(delta_hr) * combustivel_reagido
    return q_comb
def calcular_q_util(q_comb, q_chamine):
    return q_comb - q_chamine
def calcular_eficiencia(q_util,q_comb):
    if q_comb == 0:
        return 0
    return 100*q_util / q_comb
# FUNÇÃO PRINCIPAL DA SIMULAÇÃO
def executar_simulacao(
    combustivel_nome,
    vazao,
    conversao,
    seletividade,
    excesso_ar,
    T_chamine):   
    resultado_massa = calcular_balanco_massa(
        combustivel_nome=combustivel_nome,
        mols_comb_entrada=vazao,
        excesso_ar=excesso_ar,
        conversao_pct=conversao,
        seletividade_co2_pct=seletividade) 
    # Potência liberada
    q_comb = calcular_q_comb(
        combustivel_nome,
        resultado_massa["combustivel_reagido"],
        seletividade)
     # Perda pela chaminé
    q_chamine = calcular_q_chamine(
        resultado_massa["correntes_saida"],
        T_chamine)
       # Calor útil
    q_util = calcular_q_util( q_comb,q_chamine)
     # Eficiência
    eficiencia = calcular_eficiencia(q_util,q_comb)
    resultado_massa["tipo_base"] = {
        "umida": "Com H₂O",
        "seca": "Sem H₂O"
    }
    return {
        **resultado_massa,
        # ENERGIA
        "q_comb": q_comb,
        "q_chamine": q_chamine,
        "q_util": q_util,
        "eficiencia": eficiencia }
resultado = executar_simulacao(
    combustivel_nome="CH4",
    vazao=100,
    conversao=100,
    seletividade=100,
    excesso_ar=0,
    T_chamine=25)
print(resultado)
