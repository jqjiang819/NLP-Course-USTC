# Code for Lab2

This code is for Named Entity Recognition(NER).

- The codes are only for data pre-processing and result evaluation, and the model training and testing part is using the CRF++ tools.

## Notes

Before running the code, you should specify the CRF++ binary path and the template path in `lab2.py`

```python
__CRFPP_LEARN_EXEC__ = 'YOUR_CRF_LEARN_EXECUTABLE'
__CRFPP_TEST_EXEC__ = 'YOUR_CRF_TEST_EXECUTABLE'
__CRFPP_TEMPL_PATH__ = 'YOUR_TEMPLATE_FILE'
```

If you only want to train a model or simply test a current model, you should specify the action. Otherwise the program will run both training and testing by default.

When only training a model:

```bash
python3 lab2.py train
```

When only testing a model:

```bash
python3 lab2.py test
```

**Notice:** you should specify the model path in `lab2.py` when testing a pre-trained model.
