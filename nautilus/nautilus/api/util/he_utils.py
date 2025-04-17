import tenseal as ts

def create_ckks_context():
    context = ts.context(

        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2 ** 40
    context.generate_galois_keys()
    return context

def save_context(context, file_path):
    with open(file_path, 'wb') as f:
        f.write(context.serialize())

def load_context(file_path):
    with open(file_path,'rb') as f:
        return ts.context_from(f.read())

