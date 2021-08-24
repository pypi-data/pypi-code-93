import tensorflow as tf

class TransLayer(tf.keras.layers.Layer):

    def __init__(self, features_columns):
        super(TransLayer, self).__init__()
        self._tra_sp_col, self._tra_nu_col, self._gam_sp_col, self._gam_nu_col = self.get_feature_col(features_columns)
        self.tra_sparse_features = tf.keras.layers.DenseFeatures(self._tra_sp_col)
        self.tra_dense_features = tf.keras.layers.DenseFeatures(self._tra_nu_col)
        self.game_sparse_features = tf.keras.experimental.SequenceFeatures(self._gam_sp_col)
        self.game_dense_features = tf.keras.experimental.SequenceFeatures(self._gam_nu_col)
        self.game_flatten = tf.keras.layers.Flatten()

    def get_feature_col(self, fea_col):
        #get trans fea_col
        key_tra = dict()
        for i in range(len(fea_col['trans'])):
            k = fea_col['trans'][i].key
            key_tra[k]=i
        tra_sp_col = []
        for col in tensordata.sparse_features['trans']:
            k = key_tra.get(col)
            embedded = tf.feature_column.embedding_column(fea_col['trans'][k], dimension=1)
            tra_sp_col.append(embedded)
        tra_nu_col = []
        for col in tensordata.dense_features['trans']:
            k = key_tra.get(col)
            tra_nu_col.append(fea_col['trans'][k])

        #get games fea_col
        key_gam = dict()
        for i in range(len(fea_col['games'])):
            k = fea_col['games'][i].name
            key_gam[k]=i
        gam_sp_col = []
        for col in tensordata.sparse_features['games']:
            k = key_gam.get(col)
            embedded = tf.feature_column.embedding_column(fea_col['games'][k], dimension=1)
            gam_sp_col.append(embedded)
        gam_nu_col = []
        for col in tensordata.dense_features['games']: 
            if col != 'trans_id':
                k = key_gam.get(col)
                gam_nu_col.append(fea_col['games'][k])

        return tra_sp_col, tra_nu_col, gam_sp_col, gam_nu_col

    def call(self, inputs):
        #trans dataset transform
        tra_sp = self.tra_sparse_features(inputs[0][0])
        tra_nu = self.tra_dense_features(inputs[0][1])
        trainable_t = tf.keras.layers.concatenate([tra_sp, tra_nu])

        #game dataset transform
        gamsp = inputs[1][0]
        #ragged tensor to sparse tensor
        for col in gamsp:
            gamsp[col] = gamsp[col].to_sparse()
        gam_sp, gam_sp_len = self.game_sparse_features(gamsp)
        gam_sp = self.game_flatten(gam_sp)
        gam_sp = tf.reshape(gam_sp,shape=[-1,6])

        gamnu = inputs[1][1]
        #teagged tensor to sparse tensor
        for col in gamnu:
            gamnu[col] = gamnu[col].to_sparse()
        gam_nu, gam_nu_len = self.game_dense_features(gamnu)
        #reduce_mean for games info
        gam_nu_rm = tf.reduce_mean(gam_nu, axis=1)
        gam_nu_rm = self.game_flatten(gam_nu_rm)
        gam_nu_rm = tf.reshape(gam_nu_rm,shape=[-1,15])
        trainable_g = tf.keras.layers.concatenate([gam_sp, gam_nu_rm])

        trainable = tf.keras.layers.concatenate([trainable_t, trainable_g])

        return trainable
