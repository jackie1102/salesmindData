
/**
 * 打开所在行业
 * */
function open_industry(id) {
    layer.open({
        type:2,
        area: ['700px', '550px'],
        content: '/spider/open_liepin_industry/?id='+id
    });
}
/**
 * 打开地区
 * */
function open_area(id) {
    layer.open({
        type:2,
        area: ['910px', '490px'],
        content: '/spider/open_liepin_area/?id='+id
    });
}
/**
 * 打开职能
 */
function open_jobs(id){
    layer.open({
        type:2,
        area: ['1100px', '490px'],
        content: '/spider/open_liepin_jobs/?id='+id
    });
}