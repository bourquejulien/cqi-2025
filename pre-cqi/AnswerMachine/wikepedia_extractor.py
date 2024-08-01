import wikipedia

# Obtenir 1000 articles aléatoires dans Wikipedia
titres = []
while len(titres) < 10000:
    titres += wikipedia.random(500)

# Obtenir un sommaire de chaque article et l'enregistrer dans un fichier
iter = 0
for titre in titres:
    try:
        with open(f"source/{iter}.txt", "w+") as f:
            f.write(wikipedia.summary(titre))
            iter += 1
    except:
        pass
    finally:
        if iter == 1000:
            break
