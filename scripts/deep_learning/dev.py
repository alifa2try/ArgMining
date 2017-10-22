from argminingdeeplearning.loaders import vocabulary_builder
from argminingdeeplearning.loaders.dataset_loader import load_dataset
import argparse
import logging
import time
import numpy as np
from argminingdeeplearning.keras_models import lstm
from sklearn.metrics import f1_score
from pandas_confusion import ConfusionMatrix



def config_argparser():
    argparser = argparse.ArgumentParser(description='ArgMining Deep Learning')
    argparser.add_argument('-subtask', type=str, required=True, help='Name of the subtask')
    argparser.add_argument('-kerasmodel', type=str, default='lstm')
    argparser.add_argument('-padding_length', type=int, help='Padding length of each input sequence', default=20)
    argparser.add_argument('-batch_size', type=int, default=32)
    argparser.add_argument('-epochs', type=int, default=5)
    # argparser.add_argument('-hilbert', dest='hilbert', action='store_true')
    # argparser.set_defaults(hilbert=False)
    return argparser.parse_args()


if __name__ == '__main__':
    t0 = time.time()
    time_string = time.strftime('%Y%m%d_%H%M%S')
    logger = logging.getLogger()
    arguments = config_argparser()
    train_path = 'data/THF/sentence/subtask{}_v3_train.json'.format(arguments.subtask)
    test_path = 'data/THF/sentence/subtask{}_v3_test.json'.format(arguments.subtask)
    number_of_classes = 2 if arguments.subtask == 'A' else 3
    word_to_index_mapping, index_to_embedding_maping = vocabulary_builder.create_mappings(train_path)
    X_train, Y_train, train_unique_ids, Y_train_indices = load_dataset(train_path, word_to_index_mapping,
                                                                       arguments.subtask,
                                                                       arguments.padding_length)

    X_test, Y_test, test_unique_ids, Y_test_indices = load_dataset(test_path, word_to_index_mapping, arguments.subtask,
                                                                   arguments.padding_length)
    print(X_train)
    print(X_train.shape)
    print(Y_train)
    print(Y_train.shape)

    model = lstm.lstm_embedding_empty(number_of_classes)

    print('Train...')
    model.fit(X_train, Y_train,
              batch_size=arguments.batch_size,
              epochs=arguments.epochs,
              verbose=1,
              validation_data=(X_test, Y_test))
    score, acc = model.evaluate(X_test, Y_test, batch_size=arguments.batch_size)

    y_prediction = model.predict(X_test, batch_size=arguments.batch_size)

    y_prediction_classes = np.argmax(y_prediction, axis=1)
    print(y_prediction_classes)
    print()
    print('Test score:', score)
    print('Test accuracy:', acc)

    f1 = f1_score(Y_test_indices, y_prediction_classes, average=None)
    f1_mean = np.mean(f1)
    print("Micro-averaged F1: {}".format(f1_mean))
    print("Individual scores: {}".format(f1))
    print("Confusion matrix:")
    print(ConfusionMatrix(Y_test_indices, y_prediction_classes))


    output_path_base = 'results/sentence_deeplearning/temp/{}_{}_{}'.format(arguments.subtask,
                                                                            arguments.kerasmodel,
                                                                            time_string)

    prediction_file = output_path_base + '.predictions'
    with open(prediction_file, 'w') as prediction_handler:
        prediction_handler.write('{}\t{}\t{}\n'.format("UniqueID", "Gold_Label", "Prediction"))
        for index, val in enumerate(test_unique_ids):
            prediction_handler.write('{}\t{}\t{}\n'.format(val, Y_test_indices[index], y_prediction_classes[index]))
    score_file = output_path_base + '.score'
    with open(score_file, 'w') as score_handler:
        score_handler.write("Micro-averaged F1: {}\n".format(f1_mean))
        score_handler.write("Individual scores: {}\n".format(f1))
        score_handler.write("Confusion matrix:\n")
        score_handler.write(str(ConfusionMatrix(Y_test_indices, y_prediction_classes)))

    print("Total execution time in %0.3fs" % (time.time() - t0))
    print("*****************************************")
