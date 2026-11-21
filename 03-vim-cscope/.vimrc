" Vim and cscope workbench.
set nocompatible
let s:root = expand('<sfile>:p:h')
let s:bundled = s:root !=# expand('~') && isdirectory(s:root . '/.vim/pack/workbench/start')
if s:bundled
    let &runtimepath = escape(s:root . '/.vim', ',') . ',' . escape($VIMRUNTIME, ',')
    let &packpath = &runtimepath
    let s:gruvbox = s:root . '/.deps/gruvbox'
    if isdirectory(s:gruvbox)
        let &runtimepath .= ',' . escape(s:gruvbox, ',')
    endif
endif
set number
set tabstop=4
set shiftwidth=4
set softtabstop=4
set autoindent
set smartindent
set hlsearch
set incsearch
set ignorecase
set smartcase
set showmatch
set cursorline
set scrolloff=3
set ruler
set autoread
set updatetime=300
set splitright
set splitbelow
set hidden
set nopaste
let mapleader = '\'

syntax enable
filetype plugin indent on
set background=dark
if !s:bundled || isdirectory(s:gruvbox)
    colorscheme gruvbox
else
    echomsg 'Run sh bootstrap.sh from the workbench directory to install Gruvbox and fzf.'
endif

" Use the matching fzf runtime and executable.
let s:fzf = s:bundled ? s:root . '/.deps/fzf' : expand('~/.fzf')
if isdirectory(s:fzf)
    let &runtimepath .= ',' . escape(s:fzf, ',')
    if index(split($PATH, ':'), s:fzf . '/bin') < 0
        let $PATH = s:fzf . '/bin:' . $PATH
    endif
endif
let $FZF_DEFAULT_COMMAND = 'rg --files --hidden --glob "!.git"'
let g:fzf_layout = { 'down': '42%' }
let g:fzf_vim = {'listproc': { list -> fzf#vim#listproc#quickfix(list) }}

nnoremap <silent> <C-p> :Files<CR>
nnoremap <silent> <leader>r :Rg<CR>
nnoremap <silent> <leader>t :Tags<CR>
nnoremap <silent> <leader>j :Jumps<CR>

" Tabpages retain their window layout.
nnoremap <silent> <C-k> :tabprevious<CR>
nnoremap <silent> <C-l> :tabnext<CR>

let g:tagbar_sort = 0
nnoremap <silent> <F8> :TagbarToggle<CR>

" Explicit saves and loads in the current project.
let g:bookmark_save_per_working_dir = 1
let g:bookmark_auto_save = 0
let g:bookmark_center = 1
nnoremap <silent> <F6> :BookmarkSave .bookmark<CR>
nnoremap <silent> <F7> :BookmarkLoad .bookmark<CR>

" Airline owns the active status line. This is the native fallback.
set laststatus=2
set statusline=%<%f\ %m%=%y\ [%p%%]\ %l:%c
let g:airline_powerline_fonts = 0
let g:airline_theme = 'understated'
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_buffers = 0

set tags=./tags,tags;
if has('cscope')
    set cscopequickfix=c-,d-,e-,g-,i-,s-,t-
    if filereadable('cscope.out') && !cscope_connection(2, fnamemodify('cscope.out', ':p'))
        silent cs add cscope.out
    endif

    " Ctrl-backslash, followed by the cscope query type.
    for s:query in ['s', 'g', 'c', 't', 'e', 'd']
        execute 'nnoremap <silent> <C-\>' . s:query . ' :cs find ' . s:query
            \ . " <C-R>=expand('<cword>')<CR><CR>"
    endfor
    unlet s:query
    nnoremap <silent> <C-\>f :cs find f <C-R>=expand('<cfile>')<CR><CR>
    nnoremap <silent> <C-\>i :cs find i <C-R>=expand('<cfile>')<CR><CR>

    " Run from the project root. Regenerate cscope.files separately when its file set changes.
    function! s:RefreshCscope() abort
        " -u also picks up edits made in the same second as the previous build.
        let l:output = system('cscope -Rbq -u 2>&1')
        if v:shell_error
            echohl ErrorMsg
            echomsg 'cscope rebuild failed. ' . trim(l:output)
            echohl None
            return
        endif
        if cscope_connection(2, fnamemodify('cscope.out', ':p'))
            cs reset
        else
            cs add cscope.out
        endif
        echomsg 'cscope index refreshed'
    endfunction
    nnoremap <silent> <F5> :call <SID>RefreshCscope()<CR>
endif

function! s:ToggleQuickfix() abort
    if getqflist({'winid': 0}).winid
        cclose
    elseif !empty(getqflist())
        copen
    else
        echo 'quickfix is empty'
    endif
endfunction

nnoremap <silent> <F3> :call <SID>ToggleQuickfix()<CR>
augroup PresenterQuickfix
    autocmd!
    autocmd FileType qf wincmd J
augroup END

" Keep deletes and changes from overwriting the unnamed yank register.
nnoremap x "_x
nnoremap dd "_dd
nnoremap D "_D
nnoremap cc "_cc
nnoremap C "_C
nnoremap s "_s
nnoremap S "_S
