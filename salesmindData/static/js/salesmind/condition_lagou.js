/**
 * Created by Administrator on 2018/2/26.
 */
/**
 *打开行业领域
 */
function open_lagou_industry() {
    layer.open({
        type:2,
        area: ['500px', '380px'],
        content: '/spider/open_lagou_industry/'
    });
}


/**
 *打开公司地点
 */
function open_lagou_area() {
    layer.open({
        type:2,
        area: ['800px', '500px'],
        content: '/spider/open_lagou_area/'
    });
}