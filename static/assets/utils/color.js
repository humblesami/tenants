function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {    
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function rgbStringToHex(rgb) {    
    rgb = rgb.replace('rgb(','');
    rgb = rgb.replace(')','');
    rgb = rgb.split(',');
    var r = parseInt(rgb[0]);
    var g = parseInt(rgb[1]);
    var b = parseInt(rgb[1]);
    return rgbToHex(r, g, b);
}

function background_color_to_hex(el) {
    rgb = el.style.backgroundColor;
    //console.log(rgb);
    rgb = rgb.replace('rgb(','');
    rgb = rgb.replace(')','');
    //console.log(rgb);
    rgb = rgb.split(',');
    //console.log(rgb);
    var r = parseInt(rgb[0]);
    var g = parseInt(rgb[1]);
    var b = parseInt(rgb[1]);
    //console.log(r,g, b);
    var hex = componentToHex(r) + componentToHex(g) + componentToHex(b);
    //console.log(hex);
    return hex;
}
function background_color_to_hashed_hex(el) {
    var hex = background_color_to_hex(el);
    hex = '#'+hex;
    return hex;
}

function isDarkOrLight(color)
{
    // Variables for red, green, blue values
    var r, g, b, hsp;
    
    // Check the format of the color, HEX or RGB?
    if (color.match(/^rgb/)) {

        // If HEX --> store the red, green, blue values in separate variables
        color = color.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+(?:\.\d+)?))?\)$/);
        
        r = color[1];
        g = color[2];
        b = color[3];
    } 
    else {
        
        // If RGB --> Convert it to HEX: http://gist.github.com/983661
        color = +("0x" + color.slice(1).replace( 
        color.length < 5 && /./g, '$&$&'));

        r = color >> 16;
        g = color >> 8 & 255;
        b = color & 255;
    }
    
    // HSP (Highly Sensitive Poo) equation from http://alienryderflex.com/hsp.html
    hsp = Math.sqrt(
    0.299 * (r * r) +
    0.587 * (g * g) +
    0.114 * (b * b)
    );

    // Using the HSP value, determine whether the color is light or dark
    if (hsp>127.5) {

        return 'light';
    } 
    else {

        return 'dark';
    }
}

window['color_functions'] = {
    componentToHex: componentToHex,
    rgbToHex: rgbToHex,
    rgbStringToHex: rgbStringToHex,
    background_color_to_hex: background_color_to_hex,
    isDarkOrLight: isDarkOrLight
};