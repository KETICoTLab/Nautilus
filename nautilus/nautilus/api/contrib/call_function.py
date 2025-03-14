# contribution call function
from client_contribution.individual import nt_contrib_individual

def nt_contrib_evaluation(results, mode=None):
    #client contrib evaluation

    contrib_mode_list = ['individual','loo','overall_shap','shap','optimized_shap','custom']
    
    if mode == None:
        print('[ Nautilus INFO ] contribution evaluation is not defined')
        return
    
    if mode not in contrib_mode_list:
        print('[ Nautilus ERROR ] contribution evaluation mode cannot be identified ')
        return
    
    if mode == 'individual':
        # individual contribution evaluation
        client_contrib_res = nt_contrib_individual(results, mode)
        return client_contrib_res
    elif mode == 'loo':
        # loo contribution evaluation
        return
    elif mode == 'overall_shap':
        # over all shap contribution evaluation
        return
    elif mode == 'shap':
        # shap contribution evaluation
        return
    elif mode == 'optimized_shap':
        # optimized shap  contribution evaluation
        return
    elif mode == 'custom':
        # custom  contribution evaluation
        return
    else:
        print('[ Nautilus Error ] Mode is not defined')
        return
