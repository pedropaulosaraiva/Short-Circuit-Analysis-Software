from analisador_sep.numero_pu import crec, cpolar

v_t0_menos_bar_1 = [
    cpolar(1.0290,11.5276),
    cpolar(0.9852,6.0130),
    cpolar(0.9824,4.6215),
    cpolar(0.9817,3.8909),
    cpolar(0.9859,4.0049),
    cpolar(1.0355,9.6164),
    cpolar(0.9740,3.2654),
    cpolar(0.9636,-0.9988),
    cpolar(0.9434,-7.2417),
]

v_t0_menos_bar_2 = [crec(vo*cpolar(1,-30)) for vo in v_t0_menos_bar_1]

for index, vo in enumerate(v_t0_menos_bar_2, start=1):
    mag, phase = vo
    print(f"V_{index} = {mag: 1.2f}<{phase: 2.0f}°")