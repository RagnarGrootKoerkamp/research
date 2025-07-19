;;; build.el --- Minimal emacs installation to build the website -*- lexical-binding: t -*-
;; Authors: Bruno Henriques <4727729+bphenriques@users.noreply.github.com>
;; Modified from: https://github.com/bphenriques/knowledge-base/blob/master/tools/init.el

;;; Commentary:
;;; - Requires BASE_DIR environment variable
;;
;; Notes:
;; * This is not a package.
;;; Code:

(require 'subr-x)

                                        ; (toggle-debug-on-error)                                       ;; Show debug information as soon as error occurs.
(setq
 make-backup-files nil                                        ;; Disable "<file>~" backups.
 )

(defconst base-dir
  (let* ((env-key "BASE_DIR")
         (env-value (getenv env-key)))
    (if (and env-value (file-directory-p env-value))
        env-value
      (error (format "%s is not set or is not an existing directory (%s)" env-key env-value)))))

;;;
;;; Setup packages using straight.el: https://github.com/raxod502/straight.el
;;;
;;; Leads to better reproducible builds as the versions are pinned.
(defvar bootstrap-version)
(let ((bootstrap-file
       (expand-file-name "straight/repos/straight.el/bootstrap.el" user-emacs-directory))
      (bootstrap-version 5))
  (unless (file-exists-p bootstrap-file)
    (with-current-buffer
        (url-retrieve-synchronously
         "https://raw.githubusercontent.com/raxod502/straight.el/develop/install.el"
         'silent 'inhibit-cookies)
      (goto-char (point-max))
      (eval-print-last-sexp)))
  (load bootstrap-file nil 'nomessage))

(setq straight-use-package-by-default t)
(straight-use-package 'use-package)
(straight-use-package 'org)

;;;
;;; Setup packages
;;;

(use-package ox-hugo
  :straight (:type git :host github :repo "kaushalmodi/ox-hugo" :nonrecursive t))

(use-package citeproc
  :straight (:type git :host github :repo "andras-simonyi/citeproc-el" :nonrecursive t))

(setf org-hugo-base-dir base-dir)

                                        ; Disable auto-inserting References section heading.
                                        ; https://ox-hugo.scripter.co/doc/org-cite-citations/#org-radio--CSL-formatted-exports
                                        ; https://github.com/kaushalmodi/ox-hugo/issues/679
;; (with-eval-after-load 'ox-hugo
;;   (plist-put org-hugo-citations-plist :bibliography-section-heading ""))

                                        ; Auto-prefix type (figure/table) of links.
                                        ; https://ox-hugo.scripter.co/doc/linking-numbered-elements/#fnref:1
(setq org-hugo-link-desc-insert-type t)

                                        ; Use CSL by default
(setq org-cite-export-processors '((t csl)))

(setq org-cite-global-bibliography (list (expand-file-name "references.bib")))
(setq org-hugo-base-dir (expand-file-name "."))

(setq user-full-name "Ragnar Groot Koerkamp")

;;;
;;; org-special-blocks-extra
;;;
(use-package org-special-block-extras
  :ensure t
  ;; Loads a bunch of bloat, but required to make the things below work.
  :hook (org-mode . org-special-block-extras-mode)
  )

(org-mode)

(defmacro special-block-labels-push (prefix label)
  (let ((labels (format "special-block-%s-labels" prefix))
        (labels-cdr (format "special-block-%s-labels-cdr" prefix)))
    `(let ((label (list (format "%s" ,label))))
       (setq ,(intern labels-cdr)
             (if ,(intern labels-cdr)
                 (setcdr ,(intern labels-cdr) label)
               (setq ,(intern labels) label))))))




(defmacro defspeciallink (name display-name prefix)
  `(progn
     (defvar ,(intern (format "special-block-%s-labels" prefix)) '()) ; to store this theroem labels
     (defvar ,(intern (format "special-block-%s-labels-cdr" prefix)) nil)

     (org-defblock ,prefix (ref nil) ()
                   ,(format "Reference a %s special block." name)
                   (format
                    (cond
                     ((org-export-derived-backend-p org-export-current-backend 'latex)
                      ,(format "\\ref{%s:%%s}" prefix)) ; use standard ref in LateX
                     ((org-export-derived-backend-p org-export-current-backend 'html)
                      ,(format "<a href=\"#%s:%%s\">%s %%d</a>" prefix display-name))) ; in HTML the number has to be print manually, finding the position of the label in the list
                    ref (1+ (cl-position (format "%s" ref) ,(intern (format "special-block-%s-labels" prefix)) :test 'equal)))))) ; sum one because lists are zero based

(defmacro deftheorem (name display-name prefix)
  "Defines a new theorem type called NAME (rendered as DISPLAY-NAME in HTML) which labels start with PREFIX.
Usage:
,#+BEGIN_name Title :label lbl
....
,#+END_name
As can be seen in [[prefix:lbl]]
                "
  `(progn
     (defspeciallink ,name ,display-name ,prefix)

     (org-defblock ,name (title "TITLE" label nil unnumbered nil)
                   ,(format "Define %s special block." name)
                   (unless unnumbered (special-block-labels-push ,prefix label)) ; add label to list
                   (cond
                    ((org-export-derived-backend-p org-export-current-backend 'latex)
                     (format
                      (concat ,(format "\\begin{%s" name) (when unnumbered "*") "}"
                              ,(format "[%%s]\\label{%s:%%s}" prefix)
                              "\n%s"
                              ,(format "\\end{%s" name) (when unnumbered "*") "}")
                      (or title "") (or label "") contents))
                    ((org-export-derived-backend-p org-export-current-backend 'html)
                     (format
                      (concat ,(format "<div id=\"%s:%%s\" class=\"special-block %s\"><span class=\"special-block-title\"><span class=\"special-block-number\">%s" prefix name display-name)
                              (unless unnumbered (format " %d" (length ,(intern (format "special-block-%s-labels" prefix)))))
                              "</span>"
                              (when title " <span class=\"special-block-name\">") "%s" (when title "</span>") ".</span>"
                              ,(format "%%s</div>"))
                      (or label "") (or title "") contents))
                    )
                   )))

(deftheorem definition "Definition" dfn)
(deftheorem newdefinition "Definition" dfn)
(deftheorem theorem "Theorem" thm)
(deftheorem mytheorem "Theorem" thm)
(deftheorem lemma "Lemma" lem)
(deftheorem problem "Problem" prob)
(deftheorem openproblem "Open problem" prob)
(deftheorem conjecture "Conjecture" conj)
(deftheorem algorithm "Algorithm" alg)

;; Reset special-block-{theorem,definition}-labels{-cdr} before export.
(add-hook 'org-export-before-parsing-functions
          (lambda (backend)
            (setq special-block-thm-labels '())
            (setq special-block-thm-labels-cdr nil)
            (setq special-block-theorem-labels '())
            (setq special-block-theorem-labels-cdr nil)
            (setq special-block-lemma-labels '())
            (setq special-block-lemma-labels-cdr nil)
            (setq special-block-mytheorem-labels '())
            (setq special-block-mytheorem-labels-cdr nil)
            (setq special-block-dfn-labels '())
            (setq special-block-dfn-labels-cdr nil)
            (setq special-block-definition-labels '())
            (setq special-block-definition-labels-cdr nil)
            (setq special-block-newdefinition-labels '())
            (setq special-block-newdefinition-labels-cdr nil)
            (setq special-block-prob-labels '())
            (setq special-block-prob-labels-cdr nil)
            (setq special-block-problem-labels '())
            (setq special-block-problem-labels-cdr nil)
            (setq special-block-openproblem-labels '())
            (setq special-block-openproblem-labels-cdr nil)
            (setq special-block-conj-labels '())
            (setq special-block-conj-labels-cdr nil)
            (setq special-block-conjecture-labels '())
            (setq special-block-conjecture-labels-cdr nil)
            (setq special-block-alg-labels '())
            (setq special-block-alg-labels-cdr nil)
            (setq special-block-algorithm-labels '())
            (setq special-block-algorithm-labels-cdr nil)
            ))



;;;
;;; Public functions
;;;

(defun build/export-all ()
  "Export all org-files (including nested) under base-org-files."
  (let ((search-path (file-name-as-directory base-dir)))
    (message (format "[build] Looking for files at %s" search-path))
    (dolist (org-file (directory-files-recursively search-path "\.org$" nil (lambda (x) (and (not (string-match-p "emacs" x)) (not (string-match-p "submodule" x))))))
      (with-current-buffer (find-file org-file)
        (message (format "[build] Exporting %s" org-file))
        (org-hugo-export-wim-to-md :all-subtrees nil nil nil)))
    (message "Done!")))

(provide 'build/export-all)

;;; init.el ends here
