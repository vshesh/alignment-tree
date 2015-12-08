from glob import glob
import codecs, sys, time
from nltk import AlignedSent
from nltk.translate.ibm1 import IBMModel1

if __name__ == '__main__':
  start = time.time()
  foreign_file, english_file, output_file = sys.argv[1:]
  bitext = []
  with codecs.open(english_file, encoding="utf8") as english, codecs.open(foreign_file, encoding="utf8") as foreign:
    for e, f in zip(english, foreign):
      bitext.append(AlignedSent(e.encode(encoding='ascii',errors='xmlcharrefreplace').split(), f.encode(encoding='ascii',errors='xmlcharrefreplace').split()))
  ibm1 = IBMModel1(bitext, 10)

  with open(output_file, 'w') as f1:
    for a in bitext:
      aligned = a
      alignment = " ".join([ i for i in a.alignment.__repr__()[11:-2].replace("),", "").replace(")", "").replace("(", "").replace(", ", "-").split() if "None" not in i])
      f1.write(" ||| ".join([" ".join(aligned.words), " ".join(aligned.mots), alignment]) + '\n')
  
  print 'time: ', time.time() - start