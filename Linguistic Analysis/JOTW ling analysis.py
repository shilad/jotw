import gensim
import smart_open
from sklearn.cluster import KMeans
import numpy as np
from scipy.spatial.distance import cdist


train_corpus = []
comment_id = []

with smart_open.smart_open('commentcorpus.csv', encoding="iso-8859-1") as f:
    for i, line in enumerate(f):
        # For training data, add tags
        if len(line.split()[0].split('"')) == 4:
            train_corpus.append(gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(' '.join(line.split()[1:])), [i]))
            comment_id.append(gensim.models.doc2vec.TaggedDocument(line.split()[0].split('"')[3], [i]))

def getKey(item):
    return item[0]

def returnKey(item):
    return item[1]

#model = gensim.models.doc2vec.Doc2Vec(size=50, min_count=10, iter=10) #vectors are length 50
#model.build_vocab(train_corpus)

#control the learning rate over the course of 10 epochs
#for epoch in range(10):
#    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.iter)
#    model.alpha -= 0.002  # decrease the learning rate
#    model.min_alpha = model.alpha  # fix the learning rate, no decay

#print(model.docvecs.doctag_syn0)
#print(model.docvecs.doctag_syn0.shape)

#model.save('./trained.model')
#model.save_word2vec_format('./trained.word2vec')

#load the doc2vec
model = gensim.models.doc2vec.Doc2Vec.load('./trained.model')
# load the word2vec
#word2vec = gensim.models.Doc2Vec.load_word2vec_format('./trained.word2vec')

textVect = model.docvecs.doctag_syn0


## K-means ##
num_clusters = 3
km = KMeans(n_clusters=num_clusters)
km.fit(textVect)
clusters = km.labels_.tolist()

#get documents
X_cluster_k_3 = []
for n in range(3):
    X_cluster_k_3.append([train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == n])
for n in range(3):
    for doc in X_cluster_k_3[n][:20]:
        print '3 clusters, ', 'cluster', n, ': random', doc.words

cluster_3_dict = {}
for n in range(3):
    cluster_3_dict["cluster{0}".format(n)] = []
    cluster_vecs = []
    for i in range(len(X_cluster_k_3[n]) - 1):
        id = X_cluster_k_3[n][i].tags
        cluster_3_dict["cluster{0}".format(n)].append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[n], (
            -1, len(km.cluster_centers_[n]))), 'cosine'), X_cluster_k_3[n][i].words))
        new_vector = model.infer_vector(X_cluster_k_3[n][i].words)
        cluster_vecs.append(new_vector)
    print '3 clusters, ', 'Most popular word in cluster', n, ':', sorted(model.wv.most_similar(cluster_vecs), key=returnKey, reverse=True)[0][0]

for key in cluster_3_dict:
    cluster_3_dict[key] = sorted(cluster_3_dict[key], key=getKey)[:20]
for key in cluster_3_dict:
    for doc in cluster_3_dict[key]:
        print '3 clusters, ', key, ': close to centroid', doc



## K-means ##
num_clusters = 5
km = KMeans(n_clusters=num_clusters)
km.fit(textVect)
clusters = km.labels_.tolist()

#get documents
X_cluster_k_5 = []
for n in range(5):
    X_cluster_k_5.append([train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == n])
for n in range(5):
    for doc in X_cluster_k_5[n][:20]:
        print '5 clusters, ', 'cluster', n, ': random', doc.words

cluster_5_dict = {}
for n in range(5):
    cluster_5_dict["cluster{0}".format(n)] = []
    cluster_vecs = []
    for i in range(len(X_cluster_k_5[n]) - 1):
        id = X_cluster_k_5[n][i].tags
        cluster_5_dict["cluster{0}".format(n)].append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[n], (
            -1, len(km.cluster_centers_[n]))), 'cosine'), X_cluster_k_5[n][i].words))
        new_vector = model.infer_vector(X_cluster_k_5[n][i].words)
        cluster_vecs.append(new_vector)
    print '5 clusters, ', 'Most popular word in cluster', n, ':', sorted(model.wv.most_similar(cluster_vecs), key=returnKey, reverse=True)[0][0]
for key in cluster_5_dict:
    cluster_5_dict[key] = sorted(cluster_5_dict[key], key=getKey)[:20]
for key in cluster_5_dict:
    for doc in cluster_5_dict[key]:
        print '5 clusters, ', key, ': close to centroid', doc

## K-means ##
num_clusters = 7
km = KMeans(n_clusters=num_clusters)
km.fit(textVect)
clusters = km.labels_.tolist()

#get documents
X_cluster_k_7 = []
for n in range(7):
    X_cluster_k_7.append([train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == n])
for n in range(7):
    for doc in X_cluster_k_7[n][:20]:
        print '7 clusters, ', 'cluster', n, ': random', doc.words

cluster_7_dict = {}
for n in range(7):
    cluster_7_dict["cluster{0}".format(n)] = []
    cluster_vecs = []
    for i in range(len(X_cluster_k_7[n]) - 1):
        id = X_cluster_k_7[n][i].tags
        cluster_7_dict["cluster{0}".format(n)].append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[n], (
            -1, len(km.cluster_centers_[n]))), 'cosine'), X_cluster_k_7[n][i].words))
        new_vector = model.infer_vector(X_cluster_k_7[n][i].words)
        cluster_vecs.append(new_vector)
    print '7 clusters, ', 'Most popular word in cluster', n, ':', sorted(model.wv.most_similar(cluster_vecs), key=returnKey, reverse=True)[0][0]
for key in cluster_7_dict:
    cluster_7_dict[key] = sorted(cluster_7_dict[key], key=getKey)[:20]
for key in cluster_7_dict:
    for doc in cluster_7_dict[key]:
        print '7 clusters, ', key, ': close to centroid', doc

## K-means ##
num_clusters = 10
km = KMeans(n_clusters=num_clusters)
km.fit(textVect)
clusters = km.labels_.tolist()

#get documents
X_cluster_k_10 = []
for n in range(10):
    X_cluster_k_10.append([train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == n])
for n in range(10):
    for doc in X_cluster_k_10[n][:20]:
        print '10 clusters, ', 'cluster', n, ': random', doc.words

cluster_10_dict = {}
for n in range(10):
    cluster_10_dict["cluster{0}".format(n)] = []
    cluster_vecs = []
    for i in range(len(X_cluster_k_10[n]) - 1):
        id = X_cluster_k_10[n][i].tags
        cluster_10_dict["cluster{0}".format(n)].append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[n], (
            -1, len(km.cluster_centers_[n]))), 'cosine'), X_cluster_k_10[n][i].words))
        new_vector = model.infer_vector(X_cluster_k_10[n][i].words)
        cluster_vecs.append(new_vector)
    print '10 clusters, ', 'Most popular word in cluster', n, ':', sorted(model.wv.most_similar(cluster_vecs), key=returnKey, reverse=True)[0][0]
for key in cluster_10_dict:
    cluster_10_dict[key] = sorted(cluster_10_dict[key], key=getKey)[:20]
for key in cluster_10_dict:
    for doc in cluster_10_dict[key]:
        print '10 clusters, ', key, ': close to centroid', doc



#print("Top terms per cluster:")
#order_centroids = model.cluster_centers_.argsort()[:, ::-1]
#terms = model.docvecs.offset2doctag
#for i in range(10):
#    print "Cluster %d:" % i,
#    for ind in order_centroids[i, :10]:
#        print ' %s' % terms[ind],
#    print

#X_cluster_0 = [train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == 0] #make a list of these three lists
#X_cluster_1 = [train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == 1]
#X_cluster_2 = [train_corpus[i] for i in range(len(train_corpus)) if clusters[i] == 2]


#cluster_0_docs = []
#cluster_1_docs = []
#cluster_2_docs = []

#for i in range(len(X_cluster_0) - 1):
#    id = X_cluster_0[i].tags
#    cluster_0_docs.append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[0], (-1, len(km.cluster_centers_[0]))), 'euclidean'), X_cluster_0[i].words))
#cluster_0_docs = sorted(cluster_0_docs, key=getKey)[:20]

#for i in range(len(X_cluster_1) - 1):
#    id = X_cluster_1[i].tags
#    cluster_1_docs.append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[1], (-1, len(km.cluster_centers_[1]))), 'euclidean'), X_cluster_1[i].words))
#cluster_1_docs = sorted(cluster_1_docs, key=getKey)[:20]

#for i in range(len(X_cluster_2) - 1):
#    id = X_cluster_2[i].tags
#    cluster_2_docs.append((cdist(model.docvecs[id], np.reshape(km.cluster_centers_[2], (-1, len(km.cluster_centers_[2]))), 'euclidean'), X_cluster_2[i].words))
#cluster_2_docs = sorted(cluster_2_docs, key=getKey)[:20]

#print cluster_0_docs[:10]
#print cluster_1_docs[:10]
#print cluster_2_docs[:10]

#for doc in cluster_0_docs:
#    print 'cluster 0: close to centroid', doc

#for doc in cluster_1_docs:
#    print 'cluster 1: close to centroid', doc

#for doc in cluster_2_docs:
#    print 'cluster 2: close to centroid', doc