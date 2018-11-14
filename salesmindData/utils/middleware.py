# coding=utf-8


class UrlPathRecordMiddleware(object):
    '''
    记录用户访问的url地址
    '''
    # 不记录的url地址列表
    url = '/sysuser/mytask/'
    # http://127.0.0.1:8000/user/address/?a=1&b=2

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        '''
        url匹配之后视图函数调用之前会被调用
        '''
        # 获取用户访问的url request.path
        urlpath = request.path
        if UrlPathRecordMiddleware.url in urlpath:
            # 记录url地址
            request.session['url_pre'] = request.get_full_path()


















