# contribution call function
from .client_contribution.individual import nt_contrib_individual
from .client_contribution.loo import nt_contrib_loo
from .client_contribution.shap import nt_contrib_shap
from .client_contribution.LeastCore import nt_contrib_leastcore
from .client_contribution.RobustVolume import nt_contrib_robust_volume

def nt_contrib_evaluation(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=None, weight_list=None):
    #client contrib evaluation
    #print('here param', evaluation_mode, initial_model, results, DEVICE, testloader, mode, weight_list)
    contrib_mode_list = ['individual','loo','overall_shap','shap','optimized_shap','leastcore','robust_volume','custom']
 
    if num_clients == 1:
        return {'site-1': 1.0}

    if evaluation_mode == None:
        print('[ Nautilus INFO ] contribution evaluation is not defined')
        return
    
    if evaluation_mode not in contrib_mode_list:
        print('[ Nautilus ERROR ] contribution evaluation mode cannot be identified ')
        return
    
    if evaluation_mode == 'individual':
        # individual contribution evaluation
        client_contrib_res = nt_contrib_individual(initial_model, results, DEVICE, testloader ,mode='s_norm')
        return client_contrib_res
    elif evaluation_mode == 'loo':
        # loo contribution evaluation
        client_contrib_res = nt_contrib_loo(initial_model, results, DEVICE, testloader, mode='basic', weight_list=None)
        return client_contrib_res
    elif evaluation_mode == 'overall_shap':
        # over all shap contribution evaluation
        return
    elif evaluation_mode == 'shap':
        # shap contribution evaluation
        client_contrib_res = nt_contrib_shap(initial_model, results, DEVICE, testloader, mode ='basic')
        return client_contrib_res
    elif evaluation_mode == 'optimized_shap':
        # optimized shap  contribution evaluation
        return
    elif evaluation_mode == 'custom':
        # custom  contribution evaluation
        return
    elif evaluation_mode == 'leastcore':
        # leastcore contribution evaluation
        client_contrib_res = nt_contrib_leastcore(initial_model, results, DEVICE, testloader,mode='basic')
        return client_contrib_res
    elif evaluation_mode == 'robust_volume':
        # robust volume contribution evaluation
        client_contrib_res = nt_contrib_robust_volume(results)
        return client_contrib_res
    else:
        print('[ Nautilus Error ] Mode is not defined')
        return
