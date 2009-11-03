from sitforc import load_csv, identify_reg

x, y = load_csv('data.csv')
identify_reg(x, y, modellib.pt3 , shift=1.8)