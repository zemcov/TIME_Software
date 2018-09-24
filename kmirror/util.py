PACKET_FORMAT = 'fd???'
DEG_TO_STEP = 0.36  # 21.6', 1296"
GEAR_RATIO = 160.0

deg_to_arcmin = lambda a: float(a) * 60.0
deg_to_arcsec = lambda a: float(a) * 3600.0
arcmin_to_deg = lambda a: float(a) / 60.0
arcsec_to_deg = lambda a: float(a) / 3600.0
sign = lambda a: 1 if a >= 0.0 else -1
deg_to_step = lambda degs: float(degs) * GEAR_RATIO / DEG_TO_STEP
step_to_deg = lambda steps: float(steps) / GEAR_RATIO * DEG_TO_STEP
ang_subtract = lambda a1, a2: 180 - abs(abs(a1 - a2) - 180)
# convention for the sign function below is a1 is the NEW update, a2 is the OLD position
# so would be similar to simply doing (a1 - a2) (IMPORTANT)
ang_subtract_sign = lambda a1, a2: sign(a2 - a1) if abs(a1 - a2) > 180.0 else sign(a1 - a2)