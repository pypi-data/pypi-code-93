import numpy as np
import lightseq.inference as lsi


def test_diverse_beam_search():
    model = lsi.Transformer(
        "query_bidword_cuda_v2/query_bidword_transformer_cuda.0.0.1/transformer.pb", 8
    )

    # test_input = np.array([[81, 30, 49998], [52, 49998, 49998]])
    test_input = np.array([[52, 49998, 49998]])

    res = model.infer(test_input, multiple_output=True)
    print(res)


if __name__ == "__main__":
    test_diverse_beam_search()
