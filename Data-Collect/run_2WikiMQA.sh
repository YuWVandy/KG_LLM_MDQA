echo "======2WikiMQA KG Construction======"
echo "======TF-IDF======"
for n_kw in 1 3 5 10 15 20 30 50 70 100 120 140 150 170 200 250 300 400 500
do
    echo 'TF-IDF' $n_kw
    python3 main.py --kg='TF-IDF' --dataset='2WikiMQA' --n_processes=16 --n_kw=$n_kw
    # python3 count_nei_overlap.py --kg='tf_idf' --dataset='2WikiMQA' --n_kw=$n_kw
done

echo "======KNN======"
for k_knn in 1 2 3 5 10 15 20 30 40 50 60 70 80 90 100
do
    echo 'KNN' $k_knn
    python3 main.py --kg='KNN' --dataset='2WikiMQA' --n_processes=64 --k_knn=$k_knn
    # python3 count_nei_overlap.py --kg='knn' --dataset='2WikiMQA' --k_knn=$k_knn
done

echo "======MDR_KNN======"
for k_knn in 1 2 3 5 10 15 20 30 40 50 60 70 80 90 100
do
    echo 'MDR-KNN' $k_knn
    python3 main.py --kg='MDR-KNN' --dataset='2WikiMQA' --n_processes=64 --k_knn=$k_knn
    # python3 count_nei_overlap.py --kg='mdr_knn' --dataset='2WikiMQA' --n_processes=64 --k_knn=$k_knn
done

echo "======TAGME======"
for prior_prob in 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1 0.0
do
    echo 'Prior Probability Threshold' $prior_prob
    python3 main.py --kg='TAGME' --dataset='2WikiMQA' --n_processes=64 --prior_prob=$prior_prob
    # python3 count_nei_overlap.py --kg='TAGME' --dataset='2WikiMQA' --n_processes=64 --prior_prob=$prior_prob
done