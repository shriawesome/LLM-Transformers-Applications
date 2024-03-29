import tensorflow as tf
import scripts.utils as utils

class PositionalEmbedding(tf.keras.layers.Layer):
    def __init__(self, vocab_size, d_model):
        super().__init__()
        self.d_model = d_model
        self.embedding = tf.keras.layers.Embedding(vocab_size, d_model, mask_zero=True)
        self.pos_encoding = utils.positional_encoding(utils.positional_encoding(length=2048, depth = d_model))
        
    def call(self, x):
        length = tf.shape(x)[1]
        x = self.embedding(x)
        # Setting the relative scale of the embeddings and positional encoding
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding[tf.newaxis,:length,:]
        return x