import pickle
pred=pickle.load(open("pred_nb.p","rb"))
print(pred[0:10])